import random
from copy import deepcopy

from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from .leaders import areas_leaders, capitals_leaders
from .country_data import CountryData


DEFAULT_REGION = "worldwide"
VALID_REGIONS = {
    "africa",
    "americas",
    "antarctic",
    "asia",
    "europe",
    "oceania",
    "worldwide",
}


def home(request):
    capitals_card = {
        "title": "Capitals",
        "description": "Errate die Hauptstädte",
        "button_text": "Zum Spiel",
        "image_path": static("images/Bern_3px.jpg"),
        "link": reverse("worldle:default_capitals"),
        "disable": False,
    }

    languages_card = {
        "title": "Languages",
        "description": "Errate die Landessprachen",
        "button_text": "Zum Spiel",
        "image_path": static("images/Languages_3px.jpg"),
        "link": reverse("worldle:default_languages"),
        "disable": False,
    }

    areas_card = {
        "title": "Areas",
        "description": "Higher Lower mit Landesflächen",
        "button_text": "Zum Spiel",
        "image_path": static("images/World-Map.jpg"),
        "link": reverse("worldle:areas"),
        "disable": False,
    }

    competitive_capitals_card = {
        "title": "Competitive Capitals",
        "description": "Errate die Hauptstädte",
        "button_text": "Zum Spiel",
        "image_path": static("images/Bern_3px.jpg"),
        "link": reverse("worldle:competitive_capitals"),
        "disable": False,
    }

    return render(
        request,
        "worldle/home.html",
        {
            "capitals_card": capitals_card,
            "languages_card": languages_card,
            "areas_card": areas_card,
            "competitive_capitals_card": competitive_capitals_card,
        },
    )


def default_capitals(request):
    return redirect(reverse("worldle:capitals", args=[DEFAULT_REGION]))


def capitals(request, region):
    if region not in VALID_REGIONS:
        raise Http404()

    entries = deepcopy(CountryData().get_csv_entries())

    if region != DEFAULT_REGION:
        entries = [
            entry for entry in entries if entry["region"].lower().strip() == region
        ]

    # Filter entries with no capitals
    entries = [entry for entry in entries if entry["capital"].strip()]

    random_row = random.choice(entries)

    country_name = random_row["name.common"].strip()
    country_cca3 = random_row["cca3"].strip().lower()
    country_image_name = f"worldle/{country_cca3}.svg"

    capitals_list = random_row["capital"].strip().split(",")
    capitals_list = list(map(str.strip, capitals_list))
    country_capital = ", ".join(capitals_list)

    return render(
        request,
        "worldle/capitals.html",
        {
            "region": region,
            "country_image_name": country_image_name,
            "country_name": country_name,
            "country_capital": country_capital,
        },
    )


@login_required
def competitive_capitals(request):
    if request.method == "GET":
        country = CountryData().get_random_countries(1, filter_empty=["capital"])[0]
        request.session["country"] = country

        score = 0
        request.session["score"] = score

        capitals_highscore = request.user.capitals_highscore

        country_cleaned = {
            "name": country["name.common"].strip(),
            "image_url": static(f"worldle/{country['cca3'].lower()}.svg"),
        }

        correct_capitals = country["capital"].strip().lower()
        correct_capitals = list(
            map(lambda capital: capital.strip(), correct_capitals.split(","))
        )
        correct_capitals = list(filter(lambda capital: capital != "", correct_capitals))
        correct_capital = random.choice(correct_capitals)

        answers = CountryData().get_random_capitals(3, exclude=correct_capital)
        answers.append(correct_capital)
        random.shuffle(answers)

        choices = {
            "A": answers[0],
            "B": answers[1],
            "C": answers[2],
            "D": answers[3],
        }

        # Leaderboard
        users = capitals_leaders()[:20]

        return render(
            request,
            "worldle/competitive_capitals.html",
            {
                "country": country_cleaned,
                "choices": choices,
                "score": score,
                "highscore": capitals_highscore,
                "users": users,
            },
        )

    elif request.method == "POST":
        country = request.session.get("country")
        user_choice = request.POST.get("choice")

        correct_answers = country["capital"].strip().lower()
        correct_answers = list(
            map(lambda capital: capital.strip(), correct_answers.split(","))
        )
        correct_answers = list(filter(lambda capital: capital != "", correct_answers))

        is_correct = user_choice in correct_answers

        if is_correct:
            request.session["score"] += 1
        else:
            request.session["score"] = 0

        score = request.session["score"]
        capitals_highscore = request.user.capitals_highscore
        if score > capitals_highscore:
            request.user.capitals_highscore = score
            request.user.save()
            capitals_highscore = score

        # generate new country
        country = CountryData().get_random_countries(1, filter_empty=["capital"])[0]
        request.session["country"] = country

        country_cleaned = {
            "name": country["name.common"].strip(),
            "image_url": static(f"worldle/{country['cca3'].lower()}.svg"),
        }

        correct_capitals = country["capital"].strip().lower()
        correct_capitals = list(
            map(lambda capital: capital.strip(), correct_capitals.split(","))
        )
        correct_capitals = list(filter(lambda capital: capital != "", correct_capitals))
        correct_capital = random.choice(correct_capitals)

        answers = CountryData().get_random_capitals(3, exclude=correct_capital)
        answers.append(correct_capital)
        random.shuffle(answers)

        choices = {
            "A": answers[0],
            "B": answers[1],
            "C": answers[2],
            "D": answers[3],
        }

        return JsonResponse(
            {
                "country": country_cleaned,
                "choices": choices,
                "score": score,
                "highscore": capitals_highscore,
                "is_correct": is_correct,
                "correct_answers": ", ".join(correct_answers).upper(),
            }
        )


def default_languages(request):
    return redirect(reverse("worldle:languages", args=[DEFAULT_REGION]))


def languages(request, region):
    if region not in VALID_REGIONS:
        raise Http404()

    entries = deepcopy(CountryData().get_csv_entries())

    if region != DEFAULT_REGION:
        entries = [
            entry for entry in entries if entry["region"].lower().strip() == region
        ]

    # Filter entries with no languages
    entries = [entry for entry in entries if entry["languages"].strip()]

    random_row = random.choice(entries)

    country_name = random_row["name.common"].strip()
    country_cca3 = random_row["cca3"].strip().lower()
    country_image_name = f"worldle/{country_cca3}.svg"

    languages_list = random_row["languages"].strip().split(",")
    languages_list = list(map(str.strip, languages_list))
    country_languages = ", ".join(languages_list)

    return render(
        request,
        "worldle/languages.html",
        {
            "region": region,
            "country_image_name": country_image_name,
            "country_name": country_name,
            "country_languages": country_languages,
        },
    )


@login_required
def areas(request):
    if request.method == "GET":
        country1, country2 = CountryData().get_random_countries(
            2, filter_empty=["area"]
        )
        request.session["country1"] = country1
        request.session["country2"] = country2

        score = 0
        request.session["score"] = score

        areas_highscore = request.user.areas_highscore

        country1_cleaned = {
            "name": country1["name.common"].strip(),
            "image_url": static(f"worldle/{country1['cca3'].lower()}.svg"),
            "area": float(country1["area"]),
        }

        country2_cleaned = {
            "name": country2["name.common"].strip(),
            "image_url": static(f"worldle/{country2['cca3'].lower()}.svg"),
        }

        # Leaderboard
        users = areas_leaders()[:20]

        return render(
            request,
            "worldle/areas.html",
            {
                "country1": country1_cleaned,
                "country2": country2_cleaned,
                "score": score,
                "highscore": areas_highscore,
                "users": users,
            },
        )

    elif request.method == "POST":
        country1 = request.session.get("country1")
        country2 = request.session.get("country2")
        user_choice = request.POST.get("choice")

        correct_answer = (
            "higher"
            if float(country2["area"]) > float(country1["area"])
            else "lower"
            if float(country2["area"]) < float(country1["area"])
            else "equal"
        )

        is_correct = correct_answer == "equal" or correct_answer == user_choice

        if is_correct:
            request.session["score"] += 1
        else:
            request.session["score"] = 0

        score = request.session["score"]
        areas_highscore = request.user.areas_highscore
        if score > areas_highscore:
            request.user.areas_highscore = score
            request.user.save()
            areas_highscore = score

        # generate new countries
        country1 = country2  # old country2 becomes new country1
        country2 = CountryData().get_random_countries(1, filter_empty=["area"])[0]
        request.session["country1"] = country1
        request.session["country2"] = country2

        country1_cleaned = {
            "name": country1["name.common"].strip(),
            "image_url": static(f"worldle/{country1['cca3'].lower()}.svg"),
            "area": float(country1["area"]),
        }

        country2_cleaned = {
            "name": country2["name.common"].strip(),
            "image_url": static(f"worldle/{country2['cca3'].lower()}.svg"),
        }

        return JsonResponse(
            {
                "country1": country1_cleaned,
                "country2": country2_cleaned,
                "score": score,
                "highscore": areas_highscore,
                "is_correct": is_correct,
            }
        )
