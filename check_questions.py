#!/usr/bin/env python
"""Script temporal para verificar preguntas en BD"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cheater.settings')
django.setup()

from ciscoapp.models import Question

# Buscar pregunta sobre host B
q = Question.objects.filter(text__icontains='host B').first()
if q:
    print(f'Pregunta encontrada!')
    print(f'Número: {q.question_number}')
    print(f'Texto: {q.text[:150]}')
    print(f'Respuestas: {q.answers.count()}')
else:
    print('Pregunta NO encontrada')

print('\n' + '='*60)

# Verificar pregunta 33 sobre LLC
q33_all = Question.objects.filter(text__icontains='subcapa LLC')
print(f'\nPreguntas con "subcapa LLC": {q33_all.count()}')
for q in q33_all:
    print(f'\n  Número: {q.question_number}')
    print(f'  Texto: {q.text[:100]}')
    print(f'  Respuestas correctas: {q.answers.filter(is_correct=True).count()}')
    for ans in q.answers.filter(is_correct=True):
        print(f'    - {ans.text[:80]}')
