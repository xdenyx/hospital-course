import os
import json
from urllib.parse import urlparse
from behave import given, when, then


def get_client(context):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_course.settings')
    import django
    django.setup()
    from django.contrib.auth import get_user_model
    from rest_framework.test import APIClient
    User = get_user_model()
    user, _ = User.objects.get_or_create(username='behave_tester')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    client = APIClient()
    client.force_authenticate(user=user)
    context.api_client = client
    return client

def path(url):
    p = urlparse(url)
    return p.path + ('?' + p.query if p.query else '')

def do(context, method, url, payload=None):
    client = get_client(context)
    fn = getattr(client, method)
    return fn(path(url), data=payload or {}, format='json')

def js(r):
    try:
        return r.json()
    except Exception:
        return json.loads(r.content.decode()) if r.content else None

def orm_create(model_path, **kwargs):
    parts = model_path.rsplit('.', 1)
    import importlib
    mod = importlib.import_module(parts[0])
    return getattr(mod, parts[1]).objects.create(**kwargs)

@given('a running API at "{base}"')
def step_base(context, base):
    context.base = base

@when('I create a patient named "{name}" with dob "{dob}"')
def step_create_patient(context, name, dob):
    r = do(context, 'post', f"{context.base}/api/patients/",
           {"full_name": name, "date_of_birth": dob})
    assert r.status_code < 400, f'HTTP {r.status_code}'
    context.patient = js(r)

@when('I create a doctor named "{name}" specialization "{spec}"')
def step_create_doctor(context, name, spec):
    from hospital.models import Doctor
    obj = Doctor.objects.create(full_name=name, specialization=spec)
    context.doctor = {'id': obj.id, 'full_name': obj.full_name}

@when('I create work category "{name}" with price {price}')
def step_create_work_category(context, name, price):
    from hospital.models import WorkCategory
    obj = WorkCategory.objects.create(name=name, price=float(price))
    context.work_category = {'id': obj.id, 'name': obj.name}

@when('I create material category "{name}" with cost_price {cost}')
def step_create_material_category(context, name, cost):
    from hospital.models import MaterialCategory
    obj = MaterialCategory.objects.create(name=name, cost_price=float(cost))
    context.material_category = {'id': obj.id}

@when('I create medicine category "{name}" with cost_price {cost}')
def step_create_medicine_category(context, name, cost):
    from hospital.models import MedicineCategory
    obj = MedicineCategory.objects.create(name=name, cost_price=float(cost))
    context.medicine_category = {'id': obj.id}

@when('I create procedure category "{name}" with cost_price {cost}')
def step_create_procedure_category(context, name, cost):
    from hospital.models import ProcedureCategory
    obj = ProcedureCategory.objects.create(name=name, cost_price=float(cost))
    context.procedure_category = {'id': obj.id}

@when('I create a request for the patient with doctor')
def step_create_request(context):
    r = do(context, 'post', f"{context.base}/api/requests/",
           {"datetime": "2026-01-01T09:00:00Z",
            "patient_id": context.patient['id'],
            "doctor_id": context.doctor['id']})
    assert r.status_code < 400, f'HTTP {r.status_code}'
    context.request = js(r)

@when('I create an appointment for that request')
def step_create_appointment(context):
    r = do(context, 'post', f"{context.base}/api/appointments/",
           {"request_id": context.request['id'], "notes": "BDD created"})
    assert r.status_code < 400, f'HTTP {r.status_code}'
    context.appointment = js(r)

@when('I add a work to the appointment using the work category')
def step_add_work(context):
    r = do(context, 'post', f"{context.base}/api/appointment-works/",
           {"appointment": context.appointment['id'],
            "work_category": context.work_category['id']})
    assert r.status_code < 400, f'HTTP {r.status_code}'
    context.work = js(r)

@when('I add {qty:d} materials to the work using the material category')
def step_add_materials(context, qty):
    for _ in range(qty):
        r = do(context, 'post', f"{context.base}/api/work-materials/",
               {"appointment_work": context.work['id'],
                "category": context.material_category['id'],
                "quantity": 1})
        assert r.status_code < 400, f'HTTP {r.status_code}'

@when('I add {qty:d} medicine to the work using the medicine category')
def step_add_medicines(context, qty):
    for _ in range(qty):
        r = do(context, 'post', f"{context.base}/api/work-medicines/",
               {"appointment_work": context.work['id'],
                "category": context.medicine_category['id'],
                "quantity": 1})
        assert r.status_code < 400, f'HTTP {r.status_code}'

@then('the response status should be {status:d}')
def step_status(context, status):
    assert context.response.status_code == status

@then('the appointment detail should contain at least 1 work')
def step_check_work(context):
    r = do(context, 'get', f"{context.base}/api/appointments/{context.appointment['id']}/")
    assert r.status_code < 400
    data = js(r)
    assert len(data.get('works', [])) >= 1
    context.work_detail = data['works'][0]

@then('the work should have materials count {mat:d} and medicines count {med:d}')
def step_check_counts(context, mat, med):
    assert len(context.work_detail.get('materials', [])) == mat
    assert len(context.work_detail.get('medicines', [])) == med