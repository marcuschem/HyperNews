from itertools import groupby
from datetime import datetime
from pathlib import Path
import json

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.views.generic import View


def transform_date(element):
    return datetime.strptime(element, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")


def group_news(news):
    sorted_news = sorted(news, key=lambda element: datetime.strptime(element["created"], "%Y-%m-%d %H:%M:%S"),
                         reverse=True)
    group_of_news = groupby(sorted_news, key=lambda element: transform_date(element["created"]))
    return {'value': [{'date': date, 'values': list(values)} for date, values in group_of_news]}


class IndexView(View):
    template_name = 'news/home.html'
    json_path = Path(settings.NEWS_JSON_PATH)

    @classmethod
    def get(cls, request, *args, **kwargs):
        with open(cls.json_path, "r") as news_file:
            news = json.load(news_file)
            try:
                search = list(filter(lambda element: request.GET.get("q") in element["title"], news))
            except TypeError:
                return render(request, template_name=cls.template_name, context=group_news(news), *args, **kwargs)
            if search:
                return render(request, template_name=cls.template_name, context=group_news(search), *args, **kwargs)
            return render(request, template_name=cls.template_name, context=group_news(news), *args, **kwargs)


class NewsWithId(View):
    template_name = 'news/news.html'
    json_path = Path(settings.NEWS_JSON_PATH)

    @classmethod
    def get(cls, request, news_id: int = 0, *args, **kwargs):
        if not news_id:
            return HttpResponseBadRequest("Ups", content_type="text/plain")
        if not cls.json_path.is_file():
            return HttpResponseNotFound("No news", content="text/plain")
        with open(cls.json_path, "r") as news_file:
            news = json.load(news_file)
            requested_news = [*filter(lambda x: x['link'] == news_id, news)]
            context = requested_news[0]
            return render(request, template_name=cls.template_name, context=context, *args, **kwargs)


class CreateNewView(View):
    template_name = 'news/form.html'
    json_path = Path(settings.NEWS_JSON_PATH)

    @classmethod
    def get(cls, request, *args, **kwargs):
        return render(request, template_name=cls.template_name, *args, **kwargs)

    @classmethod
    def post(cls, request, *args, **kwargs):
        with open(cls.json_path, "r") as current_file:
            news = json.load(current_file)
            last_link = max([item["link"] for item in news])

        with open(cls.json_path, "w") as current_file:
            new_item = dict(created=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            text=request.POST.get("text"),
                            title=request.POST.get("title"),
                            link=last_link + 1)
            news.append(new_item)
            json.dump(news, current_file)
        return redirect("/news/", *args, **kwargs)
