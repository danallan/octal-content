import json
import pdb

from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render
from apps.user_management.models import Concepts, Profile, UserCreateForm, ExerciseAttempts, ExerciseConcepts
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate, login

from lazysignup.decorators import allow_lazy_user
from lazysignup.templatetags.lazysignup_tags import is_lazy_user
from lazysignup.models import LazyUser

#TODO remove me
from django.views.decorators.csrf import csrf_exempt

from apps.cserver_comm.cserver_communicator import get_id_to_concept_dict
from aux_text import HTML_ACCT_EMAIL, TXT_ACCT_EMAIL

from apps.octal.knowledgeInference import performInference


def user_main(request):
    if not request.user.is_authenticated() or is_lazy_user(request.user):
        return redirect('/user/login?next=%s' % request.path)

    # obtain an array of learned concept ids for the user
    uprof, created = Profile.objects.get_or_create(pk=request.user.pk)
    lids = [l.id for l in uprof.learned.all()]
    sids = [s.id for s in uprof.starred.all()]
    # TODO refactor
    if len(lids) > 0:
        concepts_dict = get_id_to_concept_dict()
        lconcepts  = [concepts_dict[idval] for idval in lids if concepts_dict.has_key(idval)]
    else:
        lconcepts = []

    if len(sids) > 0:
        concepts_dict = get_id_to_concept_dict()
        sconcepts  = [concepts_dict[idval] for idval in sids if concepts_dict.has_key(idval)]
    else:
        sconcepts = []

    return render_to_response('user.html', {"lconcepts": lconcepts, "sconcepts": sconcepts}, context_instance=RequestContext(request))

@allow_lazy_user
def register(request, redirect_addr="/user"):

    # don't allow logged-in users to register a new account
    if request.user.is_authenticated and not is_lazy_user(request.user):
        return HttpResponseRedirect(redirect_addr)
        
    if request.method == 'POST':
        form = UserCreateForm(request.POST, instance=request.user)

        if form.is_valid():

            # save lazy or non-lazy acct
            if is_lazy_user(form.instance):
                user = LazyUser.objects.convert(form) 
            else:
                user = form.save()

            # create and save corresponding profile
            prof = Profile(user=user)
            prof.save()

            # send basic info email
            uname = form.cleaned_data['username']
            subject, from_email, to = 'Metacademy account successfully created', 'accounts@metacademy.org', form.cleaned_data['email']
            text_content = TXT_ACCT_EMAIL % uname
            
            html_content = HTML_ACCT_EMAIL % uname
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            
            try:
                msg.send()
            except:
                # TODO handle incorrect emails better
                print "Unable to send confirmation message to " + to
            login(request, authenticate(**form.get_credentials()))
            return HttpResponseRedirect(redirect_addr)
    else:
        form = UserCreateForm()
    return render(request, "user_management/register.html", {
        'form': form,
    })

# we may want to consider using a more structured approach like tastypi as we
# increase the complexity of the project
# or maybe just switching to class-based views would simplify this makeshift API
@allow_lazy_user
def handle_concepts(request, conceptId=""):
    """
    A simple interface for handling a user's association with a concept
    """
    rbody = json.loads(request.body) # communication payload
    method = request.method

    if method == "PUT":
        cid = rbody["id"]
        learned = rbody["learned"]
        starred = rbody["starred"]

        uprof, created = Profile.objects.get_or_create(pk=request.user.pk)
        dbConceptObj, ucreated = Concepts.objects.get_or_create(id=cid)

        if learned:
            dbConceptObj.learned_uprofs.add(uprof)
        else:
            dbConceptObj.learned_uprofs.remove(uprof)
        if starred:
            dbConceptObj.starred_uprofs.add(uprof)
        else:
            dbConceptObj.starred_uprofs.remove(uprof)

        dbConceptObj.save()

        return HttpResponse()

    else:
        return HttpResponse(status=405)

@allow_lazy_user
def handle_exercise_request(request, conceptId=""):
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
