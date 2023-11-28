from django.db import models


class Title(models.TextChoices):
    FIDE_MASTER = "FM", "FIDE Master"
    INTERNATIONAL_MASTER = "IM", "International Master"
    NATIONAL_MASTER = "NM", "National Master"
    GRANDMASTER = "GM", "Grandmaster"
    CANDIDATE_MASTER = "CM", "Candidate Master"
    WOMAN_GRANDMASTER = "WGM", "Woman Grandmaster"
    WOMAN_INTERNATIONAL_MASTER = "WIM", "Woman International Master"
    WOMAN_FIDE_MASTER = "WFM", "Woman FIDE Master"
    WOMAN_CANDIDATE_MASTER = "WCM", "Woman Candidate Master"
    WOMAN_NATIONAL_MASTER = "WNM", "Woman National Master"
    ARENA_GRANDMASTER = "AGM", "Arena Grandmaster"
    ARENA_INTERNATIONAL_MASTER = "AIM", "Arena International Master"
    ARENA_FIDE_MASTER = "AFM", "Arena FIDE Master"
    ARENA_CANDIDATE_MASTER = "ACM", "Arena Candidate Master"
    ARENA_NATIONAL_MASTER = "ANM", "Arena National Master"
    INTERNATIONAL_ARBITER = "IA", "International Arbiter"
    FIDE_ARBITER = "FA", "FIDE Arbiter"
    FIDE_SENIOR_TRAINER = "FST", "FIDE Senior Trainer"
    FIDE_TRAINER = "FT", "FIDE Trainer"
    FIDE_INSTRUCTOR = "FI", "FIDE Instructor"
    NATIONAL_INSTRUCTOR = "NI", "National Instructor"
    DEVELOPMENTAL_INSTRUCTOR = "DI", "Developmental Instructor"
    FIDE_INTERNATIONAL_ORGANIZER = "FIO", "FIDE International Organizer"


class PlayerStatus(models.TextChoices):
    CLOSED = "closed", "Closed"
    CLOSED_FAIR_PLAY = "closed:fair_play_violations", "Closed: Fair Play Violations"
    BASIC = "basic", "Basic"
    PREMIUM = "premium", "Premium"
    MOD = "mod", "Moderator"
    STAFF = "staff", "Staff"
