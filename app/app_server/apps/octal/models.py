from django.db import models
from django.contrib.auth.models import User

from apps.user_management.models import Profile
from apps.cserver_comm.cserver_communicator import get_id_to_concept_dict

class ExerciseConcepts(models.Model):
    """
    Skeleton to factor out concepts from exercise attempts
    """
    conceptId = models.CharField(max_length=10, unique=True)

    def __unicode__(self):
        return self.get_tag()

    def get_tag(self):
        if not hasattr(self, 'tag'):
            id_concept_dict = get_id_to_concept_dict()
            self.tag = id_concept_dict[self.conceptId]['tag'].encode('ascii')
        return self.tag

class ExerciseAttempts(models.Model):
    """
    Store exercise attempts for every user
    """
    uprofile  = models.ForeignKey(Profile)
    concept   = models.ForeignKey(ExerciseConcepts)
    exercise  = models.PositiveIntegerField()
    correct   = models.BooleanField()
    timestamp = models.DateTimeField(auto_now=True)
    submitted = models.BooleanField(default=False)

    def __unicode__(self):
        if self.submitted is True:
            return u'%s %i SUBMITTED %i' % (self.uprofile, self.exercise, self.correct)
        return u'%s %i NOT SUBMITTED' % (self.uprofile, self.exercise)

    def get_correctness(self):
        if self.submitted is True:
            return (self.concept.get_tag(), self.correct)
        return None
