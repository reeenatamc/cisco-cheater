from django.test import TestCase
from ciscoapp.models import Examen, Pregunta, Respuesta, ParUnir, ActivationKey
import json

# Create your tests here.

class ModelTests(TestCase):
    def setUp(self):
        # Create an exam
        self.examen = Examen.objects.create(
            nombre="Test Exam",
            url_fuente="https://example.com"
        )
        
        # Create an activation key for API tests
        self.activation_key = ActivationKey.objects.create(
            key="test-key-123",
            device_id="test-device-123",
            is_active=True
        )
    
    def test_examen_creation(self):
        """Test that examen can be created"""
        self.assertEqual(self.examen.nombre, "Test Exam")
        self.assertEqual(str(self.examen), "Test Exam")
    
    def test_pregunta_simple(self):
        """Test simple choice question"""
        pregunta = Pregunta.objects.create(
            examen=self.examen,
            numero=1,
            texto="What is Django?",
            tipo="opcion_simple",
            es_manual=False
        )
        
        Respuesta.objects.create(
            pregunta=pregunta,
            texto="A Python web framework",
            indice=1
        )
        
        self.assertEqual(pregunta.respuestas.count(), 1)
        self.assertEqual(pregunta.tipo, "opcion_simple")
    
    def test_pregunta_multiple(self):
        """Test multiple choice question"""
        pregunta = Pregunta.objects.create(
            examen=self.examen,
            numero=2,
            texto="Select all web frameworks",
            tipo="opcion_multiple",
            es_manual=False
        )
        
        Respuesta.objects.create(pregunta=pregunta, texto="Django", indice=1)
        Respuesta.objects.create(pregunta=pregunta, texto="Flask", indice=2)
        
        self.assertEqual(pregunta.respuestas.count(), 2)
    
    def test_pregunta_unir(self):
        """Test matching/drag question"""
        pregunta = Pregunta.objects.create(
            examen=self.examen,
            numero=3,
            texto="Match the following",
            tipo="unir",
            es_manual=True
        )
        
        ParUnir.objects.create(
            pregunta=pregunta,
            elemento_izquierdo="Python",
            elemento_derecho="Programming Language"
        )
        
        self.assertEqual(pregunta.pares.count(), 1)


class APITests(TestCase):
    def setUp(self):
        # Create test data
        self.examen = Examen.objects.create(nombre="API Test Exam")
        
        self.activation_key = ActivationKey.objects.create(
            key="test-key-456",
            device_id="test-device-456",
            is_active=True
        )
        
        # Simple question
        self.pregunta_simple = Pregunta.objects.create(
            examen=self.examen,
            numero=1,
            texto="1. What is Python?",
            tipo="opcion_simple"
        )
        Respuesta.objects.create(
            pregunta=self.pregunta_simple,
            texto="A programming language",
            indice=2
        )
        
        # Multiple choice question
        self.pregunta_multiple = Pregunta.objects.create(
            examen=self.examen,
            numero=2,
            texto="2. Select all databases",
            tipo="opcion_multiple"
        )
        Respuesta.objects.create(
            pregunta=self.pregunta_multiple,
            texto="PostgreSQL",
            indice=1
        )
        Respuesta.objects.create(
            pregunta=self.pregunta_multiple,
            texto="MySQL",
            indice=3
        )
        
        # Unir question
        self.pregunta_unir = Pregunta.objects.create(
            examen=self.examen,
            numero=3,
            texto="3. Match programming concepts",
            tipo="unir"
        )
        ParUnir.objects.create(
            pregunta=self.pregunta_unir,
            elemento_izquierdo="ORM",
            elemento_derecho="Object-Relational Mapping"
        )
    
    def test_buscar_simple_question_found(self):
        """Test searching for simple choice question - found"""
        response = self.client.post(
            '/buscar/',
            json.dumps({
                'device_id': 'test-device-456',
                'pregunta': '1. What is Python?'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('found'))
        self.assertEqual(data['respuesta'], [2, "A programming language"])
    
    def test_buscar_multiple_question_found(self):
        """Test searching for multiple choice question - found"""
        response = self.client.post(
            '/buscar/',
            json.dumps({
                'device_id': 'test-device-456',
                'pregunta': 'Select all databases'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('found'))
        self.assertIsInstance(data['respuesta'], list)
        self.assertEqual(data['respuesta'][0], "1, 3")
    
    def test_buscar_unir_question_found(self):
        """Test searching for matching question - found"""
        response = self.client.post(
            '/buscar/',
            json.dumps({
                'device_id': 'test-device-456',
                'pregunta': '3. Match programming concepts'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('found'))
        self.assertEqual(data['respuesta']['tipo'], 'unir')
        self.assertEqual(len(data['respuesta']['pares']), 1)
    
    def test_buscar_question_not_found(self):
        """Test searching for non-existent question"""
        response = self.client.post(
            '/buscar/',
            json.dumps({
                'device_id': 'test-device-456',
                'pregunta': 'This question does not exist'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get('found'))
        self.assertIn('no encontrada', data['respuesta'])
    
    def test_buscar_unauthorized(self):
        """Test searching without valid device_id"""
        response = self.client.post(
            '/buscar/',
            json.dumps({
                'device_id': 'invalid-device',
                'pregunta': 'test'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
