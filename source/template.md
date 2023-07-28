+++
author = "Indigo"
title = "{{ title }}"
date = "{{ date }}"
{% if tags %}
tags = [
    {% for tag in tags %}
     "{{ tag }}",
    {% endfor %}
]
{% endif %}
{% if summary %}
summary = "{{ summary }}"
{% endif %}
{% if note1 %}
note1 = "{{ note1 }}"
{% endif %}
{% if note2 %}
note2 = "{{ note2 }}"
{% endif %}
draft = false
+++

{% for paragraph in body %}
{{ paragraph | safe }}
{% endfor %}