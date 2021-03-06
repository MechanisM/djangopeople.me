from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.core.validators import RegexValidator

from social_auth.signals import pre_update
from social_auth.backends.github import GithubBackend
from social_auth.backends.twitter import TwitterBackend
from taggit.managers import TaggableManager


class UserProfile(models.Model):
    AVAILABLE_FOR = (
        (0, "Nothing"),
        (1, "Freelance/Contract work"),
        (2, "Full-time work"),
        (3, "I'm not picky."),
    )

    user = models.OneToOneField(User)
    location = models.CharField(
        blank=True,
        help_text="What you'd like others to see your location as.",
        max_length=255)
    available_for = models.PositiveSmallIntegerField(default=0,
        choices=AVAILABLE_FOR)
    point = models.PointField(blank=True, editable=False, null=True)
    bio = models.TextField(blank=True, help_text="Tell us a bit about you.")
    tags = TaggableManager(blank=True)
    github_username = models.CharField(blank=True, max_length=40,
        validators=[RegexValidator(r"^[\w-]{1,40}$")])
    bitbucket_username = models.CharField(blank=True, max_length=30,
        validators=[RegexValidator(r"^[\w-]{1,30}$")])
    twitter_username = models.CharField(blank=True, max_length=15,
        validators=[RegexValidator(r"^[\w-]{1,15}$")])
    forrst_username = models.CharField(blank=True, max_length=255,
        validators=[RegexValidator(r"^\w{1,255}$")])
    linkedin_username = models.CharField(max_length=30, blank=True,
        validators=[RegexValidator(r"^\w{5,30}$")])
    objects = models.GeoManager()

    def __unicode__(self):
        return self.user.username

    @property
    def coords(self):
        """
        Return tuple of lat,lng from GeoDjango
        """
        if self.point:
            return (self.point.get_coords()[1], self.point.get_coords()[0])
        return (None, None)

    @property
    def twitter_url(self):
        if self.twitter_username:
            return u"http://twitter.com/%s" % self.twitter_username
        return None

    @property
    def github_url(self):
        if self.github_username:
            return u"https://github.com/%s" % self.github_username
        return None

    @property
    def bitbucket_url(self):
        if self.bitbucket_username:
            return u"http://bitbucket.org/%s" % self.bitbucket_username
        return None

    @property
    def forrst_url(self):
        if self.forrst_username:
            return u"http://forrst.com/people/%s" % self.forrst_username
        return None

    @property
    def linkedin_url(self):
        if self.linkedin_username:
            return u"http://linkedin.com/in/%s" % self.linkedin_username
        return None


class Site(models.Model):
    user = models.ForeignKey(User, related_name="sites")
    site_domain = models.CharField(max_length=255,
        help_text="Include http(s)://")
    site_name = models.CharField(max_length=255)
    site_description = models.TextField(blank=True,
        help_text="Describe your involvement with the project")

    def __unicode__(self):
        return self.name


def github_user_update(sender, user, response, details, **kwargs):
    import pdb
    pdb.set_trace()

pre_update.connect(github_user_update, sender=GithubBackend)

def twitter_user_update(sender, user, response, details, **kwargs):
    profile, create = UserProfile.objects.get_or_create(user=user)

    profile.user.username = response["screen_name"]
    if create:
        profile.point = generate_point(lat=0, lng=0)
    profile.save()
    user.username = response['screen_name']
    user.save()

    return True

pre_update.connect(twitter_user_update, sender=TwitterBackend)
