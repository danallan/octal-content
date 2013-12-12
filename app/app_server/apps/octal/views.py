import json

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from lazysignup.decorators import allow_lazy_user

from apps.octal.models import ExerciseAttempts, ExerciseConcepts
from apps.cserver_comm.cserver_communicator import get_full_graph_json_str, get_id_to_concept_dict
from apps.user_management.models import Profile

from apps.octal.knowledgeInference import performInference

#TODO remove me
from django.views.decorators.csrf import csrf_exempt


def get_octal_app(request):
    if request.user.is_authenticated():
        uprof, created = Profile.objects.get_or_create(pk=request.user.pk)
        lset = set()
        sset = set()
        [lset.add(lc.id) for lc in uprof.learned.all()]
        [sset.add(sc.id) for sc in uprof.starred.all()]
        concepts = {"concepts": [{"id": uid, "learned": uid in lset, "starred": uid in sset} for uid in lset.union(sset)]}
    else:
        concepts = {"concepts": []}
    return render_to_response("octal-app.html", 
                              {
                                "full_graph_skeleton": get_full_graph_json_str(),
                                "user_data": json.dumps(concepts)
                              },
                              context_instance=RequestContext(request))

@allow_lazy_user
def handle_exercise_request(request, conceptId=""):
    #does the requested concept exist?
    concept_dict = get_id_to_concept_dict()
    if conceptId not in concept_dict: 
        return HttpResponse(status=422)

    uprof, pcreated = Profile.objects.get_or_create(pk=request.user.pk)
    excpt, ccreated = ExerciseConcepts.objects.get_or_create(conceptId=conceptId)

    qid = 0

    try:
        # try to recycle an unused attempt id
        ex = ExerciseAttempts.objects.filter(uprofile=uprof).filter(exercise=qid).get(submitted=False)
    except ExerciseAttempts.DoesNotExist:
        ex = ExerciseAttempts(uprofile=uprof, exercise=qid, concept=excpt)
        ex.save()

    q = {
            'qid': qid,
            'h': '<p>question text goes here</p>',
            't': 1, 
            'a': ["correct answer","ans2","ans3","ans4"],
            'aid': ex.pk,
        }

    return HttpResponse(json.dumps(q), mimetype='application/json')

@allow_lazy_user
@csrf_exempt #TODO remove me
def handle_exercise_attempt(request, attempt="", correct=""):
    #def handle_exercise_attempt(request, concept="", exercise="", attempt="", correct=""):
    uprof, created = Profile.objects.get_or_create(pk=request.user.pk)
    try:
        # only inject attempts if we have not submitted for this attempt
        ex = ExerciseAttempts.objects.filter(uprofile=uprof).filter(submitted=False).get(pk=attempt)
    except ExerciseAttempts.DoesNotExist, ExerciseAttempts.MultipleObjectsReturned:
        ex = None

    if request.method == "GET":
        return HttpResponse(ex)
    elif request.method == "PUT":
        # only accept data if we were waiting for it
        if ex is None:
            return HttpResponse(status=401)
        ex.correct = True if int(correct) is 1 else False
        ex.submitted = True
        ex.save()    
        return HttpResponse()
    else:
        return HttpResponse(status=405)

@allow_lazy_user
def handle_knowledge_request(request, conceptID=""):
    if request.method == "GET":
        uprof, created = Profile.objects.get_or_create(pk=request.user.pk)
        ex = ExerciseAttempts.objects.filter(uprofile=uprof).filter(submitted=True)
        r = [e.get_correctness() for e in ex.all()]
        inferences = performInference(r)
        return HttpResponse(json.dumps(inferences), mimetype='application/json')
    else:
        return HttpResponse(status=405)
