#Testing through the API: simulate that the paramters in the API is being filled
import json
import requests
import pytest
import datetime

@pytest.fixture
def baseURL():
    return("http://127.0.0.1:7890/")

@pytest.fixture
def zooWithOneAnimal(baseURL):
    requests.post(baseURL + "/animal", {"species": "tiger", "name": "ti", "age": 3})
    response = requests.get(baseURL+"/animals")
    return response.content

def test_Animals(zooWithOneAnimal):
    jo = json.loads(zooWithOneAnimal)
    print(jo)
    assert (len(jo) == 1)
    assert jo[0]["common_name"] == "ti"

@pytest.fixture
def zooWithOneEnclosure(baseURL):
    requests.post(baseURL + "/enclosure", {"name": "cage", "area": 35})
    response = requests.get(baseURL+"/enclosures")
    return response.content

@pytest.fixture
def zooWithOneEmployee(baseURL):
    requests.post(baseURL + "/employee", {"name": "Sam", "address": "Krems"})
    response = requests.get(baseURL+"/employees")
    return response.content

def test_Enclosures(zooWithOneEnclosure):
    jo = json.loads(zooWithOneEnclosure)
    assert (len(jo) == 1)
    assert jo[0]["name"] == "cage"

def test_deleteAnimal(baseURL):
    requests.post(baseURL + "/animal", {"species": "lion", "name": "alex", "age": 5})
    response1 = requests.get(baseURL + "/animals")
    jo = json.loads(response1.content)
    #I am counting on having an animal created by another test done previously
    assert len(jo) == 2
    animal_id = jo[-1]['animal_id']
    requests.delete(baseURL + f"/animal/{animal_id}")
    response = requests.get(baseURL + "/animals")
    jo1 = json.loads(response.content)
    assert len(jo1) == 1

def test_Feed(baseURL):
    requests.post(baseURL + "/animal", {"species": "lion", "name": "alex", "age": 5})
    response1 = requests.get(baseURL + "/animals")
    jo1 = json.loads(response1.content)
    animal_id = jo1[-1]['animal_id']
    print(animal_id)
    assert jo1[-1]["common_name"] == "alex"
    print(response1.json())
    assert len(response1.json()) == 2

    response2 = requests.post(baseURL + f"/animals/{animal_id}/feed") #the animal id is a path param so it should be added within the URL
    jo2 = json.loads(response2.content)
    assert jo2 == 'alex was fed'
    response3 = requests.get(baseURL + "/animals")
    jo3 = json.loads(response3.content)
    assert len(jo3[-1]["feeding_record"]) == 1


def test_Vet(baseURL):
    response = requests.get(baseURL + "/animals")
    jo1 = json.loads(response.content)
    animal_id = jo1[-1]['animal_id']

    response1 = requests.post(baseURL + f"/animals/{animal_id}/vet")
    jo2 = json.loads(response1.content)
    assert jo2 == f'Animal with ID {animal_id} had a medical checkup'
    response3 = requests.get(baseURL + "/animals")
    jo3 = json.loads(response3.content)
    assert len(jo3[-1]["medical_record"]) == 1

def test_MedicalPlan(baseURL):
    response = requests.get(baseURL + "/animals")
    jo = json.loads(response.content)
    #animal alex has been taken to the vet so I need to take to the vet the other animal called ti
    animal_id = jo[0]['animal_id']
    requests.post(baseURL + f"/animals/{animal_id}/vet")

    response1 = requests.get(baseURL + "/tasks/medical")
    response2 = requests.get(baseURL + "/tasks/medicaldates")
    jo2 = json.loads(response2.content)
    next_check = jo2[0]
    jo1 = json.loads(response1.content)
    assert jo1 == ["The next date for checking the animal: ", jo[0]['common_name'], "is: ", next_check]
    #It is not looping within all the animals, it just prints the output for the first animal in the list. This is an error I couldn´t solve
    #I think the error must be in the for loops on the zooma file

def test_Birth(baseURL):
        #obtain the animal id:
    response = requests.get(baseURL + "/animals")
    jo1 = json.loads(response.content)
    animal_id = jo1[-1]['animal_id']
    total_animals = len(jo1) #register the previous number of animals in order to check when the baby is added
        # I am considering the animals created before by other methods

        #Giving birth when the mother hasnt been assign to an enclosure:
    response1 = requests.post(baseURL + f"/animals/birth", {"animal_id": animal_id})
    jo2 = json.loads(response1.content)
    assert jo2 == f"It is necessary to assign an enclosure to the mother (home method)"

        #obtain the enclosure id:
    response2 = requests.get(baseURL + "/enclosures")
    jo3 = json.loads(response2.content)
    enclosure_id = jo3[-1]['enclosure_id']

    #Giving birth when the mother has been assign to an enclosure:
    response3 = requests.post(baseURL + f"/animals/{animal_id}/home", {"enclosure_id": enclosure_id})
    jo4 = json.loads(response3.content)
    response4 = requests.post(baseURL + f"/animals/birth", {"animal_id": animal_id})
    jo5 = json.loads(response4.content)
    assert jo5 == f"Animal with ID {animal_id} has given birth"
        #checking that the baby has been added to the list of animals in the zoo
    response5 = requests.get(baseURL + "/animals")
    jo6 = json.loads(response5.content)
    assert len(jo6)== (total_animals + 1) #checking if the list has increased by one (baby)
    assert jo6[-1]['common_name'] == 'alex' #same common_name as the mother
    assert jo6[-1]['enclosure'] == jo6[-2]['enclosure'] #same enclosure as the mother


def test_Death(baseURL):
    response = requests.get(baseURL + "/animals")
    jo1 = json.loads(response.content)
    animal_id = jo1[-1]['animal_id']
    response1 = requests.post(baseURL + f"/animals/death", {"animal_id": animal_id})
        #the animal id is a query param, I cant add it to the path.
    jo2 = json.loads(response1.content)
    assert jo2== f"Animal with ID {animal_id} is dead"
        #checking that the animal that is death is no longer in the list of animals in the zoo:
    response2 = requests.get(baseURL + "/animals")
    jo3 = json.loads(response2.content)
    assert jo1[-1] not in jo3


def test_Home(baseURL):
        #obtain the animal id:
    response = requests.get(baseURL + "/animals")
    jo1 = json.loads(response.content)
    animal_id = jo1[-1]['animal_id']
    animal_name= jo1[-1]['common_name']
        #obtain the enclosure id:
    response = requests.get(baseURL + "/enclosures")
    jo2 = json.loads(response.content)
    enclosure_id = jo2[-1]['enclosure_id']
    enclosure_name = jo2[-1]['name']

    response1 = requests.post(baseURL + f"/animals/{animal_id}/home", {"enclosure_id": enclosure_id})
        #animal id is a path param so it should be filled within the URL
        #enclosure id is a query param so it should be filled from outside the URL
    jo3 = json.loads(response1.content)
    assert jo3 == f'Animal called {animal_name} with ID {animal_id} is living in {enclosure_name} which ID is {enclosure_id}'

    response2 = requests.get(baseURL + "/animals")
    jo3 = json.loads(response2.content)
    assert jo3[-1]['enclosure'] == enclosure_name

def test_AnimalsinEnclosure(baseURL):
    response = requests.get(baseURL + "/animals")
    jo = json.loads(response.content)
    animal= jo[1]['common_name']
    #Animal alex is in enclosure cage, animal ti hasnt been assigned an enclosure
    response1 = requests.get(baseURL + '/enclosures')
    jo1= json.loads(response1.content)
    enclosure_id= jo1[0]['enclosure_id']
    assert jo[1] in jo1[0]['occupants']
    response2 = requests.get(baseURL +f'/enclosures/{enclosure_id}/animals')
    jo2 = json.loads(response2.content)
    assert jo2 == f"In the enclosure with ID {enclosure_id} are living the following animals: [{animal}] "

def test_StatsAnimals(baseURL):
    response = requests.get(baseURL + f"/animals/stats")
    jo = json.loads(response.content)
    #Testing when not all the animals are assigned to enclosures
    assert jo == 'It is necessary to assign an enclosure to every animal'

    # Testing when there are 2 animals of different species at different enclosures:
    requests.post(baseURL + "/enclosure", {"name": "pool", "area": 50})
    response = requests.get(baseURL + "/enclosures")
    jo2 = json.loads(response.content)
    enclosure_id = jo2[-1]['enclosure_id']
    enclosure_id2 = jo2[0]['enclosure_id'] #I will add another animal here
    response1 = requests.get(baseURL + f"/animals")
    jo3 = json.loads(response1.content)
    animal_id = jo3[0]['animal_id']
    animal_id2 = jo3[1]['animal_id'] #this is the animal I will change the enclosure
    requests.post(baseURL + f"/animals/{animal_id}/home", {"enclosure_id": enclosure_id})
    response3 = requests.get(baseURL + f'/enclosures')
    jo3 = json.loads(response3.content)
    assert len(jo3[0]['occupants']) == 1
    assert len(jo3[1]['occupants']) == 1
    response4 = requests.get(baseURL + f"/animals/stats")
    jo4 = json.loads(response4.content)
    assert jo4 == 'Statistics about the animals in the zoo are: Total number of animal per species is: {'+"'tiger'"+": 1,"+" 'lion'"+": 1}. The number of enclosures with animals from multiple species is: 0. The average number of animals per enclosure is: 1.0. The available space in each enclosure for every animal in it is:{"+"'cage'"+": 35.0, "+"'pool'"+": 50.0}"

    # Testing when there are 2 animals of different species at the same enclosure and 1 more animal in another enclosure:
    requests.post(baseURL + "/animal", {"species": "fish", "name": "nemo", "age": 5})
    response5 = requests.get(baseURL + "/animals")
    jo5 = json.loads(response5.content)
    animal_id_fish= jo5[-1]['animal_id']
    requests.post(baseURL + f"/animals/{animal_id2}/home", {"enclosure_id": enclosure_id})
    requests.post(baseURL + f"/animals/{animal_id_fish}/home", {"enclosure_id": enclosure_id2})
    response6 = requests.get(baseURL + f'/enclosures')
    jo6 = json.loads(response6.content)
    assert len(jo6[1]['occupants']) == 2
    assert len(jo6[0]['occupants']) == 1
    response7 = requests.get(baseURL + f"/animals/stats")
    jo7 = json.loads(response7.content)
    assert jo7 == 'Statistics about the animals in the zoo are: Total number of animal per species is: {' + "'tiger'" + ": 1," + " 'lion'" + ": 1," + " 'fish'" + ": 1}. The number of enclosures with animals from multiple species is: 1. The average number of animals per enclosure is: 1.5. The available space in each enclosure for every animal in it is:{" + "'cage'" + ": 35.0, " + "'pool'" + ": 25.0}"


def test_CleanEncl(baseURL):
    response = requests.get(baseURL + "/enclosures")
    jo = json.loads(response.content)
    enclosure_id = jo[0]['enclosure_id']
    requests.post(baseURL+ f"/{enclosure_id}/clean")
    response1 = requests.get(baseURL + "/enclosures")
    jo1 = json.loads(response1.content)
    assert len(jo1[0]['cleaning_record']) == 1



#For both methods "delete" it is neccessary to add the new ids (for enclosure and employee) as body parameters:

@pytest.fixture(scope='session')
def build_request_body2(): #create the body param
    def _build(new_enclosure_id):
        return {"new_enclosure_id": new_enclosure_id}
    return _build

@pytest.fixture(scope="session")
def authorization_token():
    return "Bearer YOUR_BEARER_TOKEN"

def test_DeleteEnclosure(baseURL, build_request_body2, authorization_token):
    response = requests.get(baseURL + "/enclosures")
    jo = json.loads(response.content)
    enclosure_id = jo[-1]['enclosure_id']
    occupant = jo[-1]['occupants'][0] #store the animal who will be moved
        #create a new enclosure who will receive the animals from the enclosure that will be deleted
    requests.post(baseURL + "/enclosure", {"name": "pool", "area": 20})
    response1 = requests.get(baseURL + "/enclosures")
    jo1 = json.loads(response1.content)
    new_enclosure_id = jo1[-1]['enclosure_id']

        #giving the new enclosure id to the API:
    api_request = build_request_body2(new_enclosure_id= new_enclosure_id)
    url = f"{baseURL}/enclosure/{enclosure_id}"
    header = {"Authorization": authorization_token}
    response2 = requests.delete(url=url, data=api_request, headers=header)

    jo2 = json.loads(response2.content)
    assert jo2 == f"Enclosure with ID {enclosure_id} was removed. It's animals were transfered to enclosure with ID {new_enclosure_id}"
    response3 = requests.get(baseURL + "/enclosures")
    jo3 = json.loads(response3.content)
    assert occupant in jo3[-1]['occupants'] #checking that the animal has been correctly changed of enclosure

def test_AnimaltoEmployee(baseURL, zooWithOneEmployee):
    jo = json.loads(zooWithOneEmployee)
    employee_id = jo[-1]['employee_id']
    response = requests.get(baseURL + "/animals")
    jo1 = json.loads(response.content)
    animal_id = jo1[-1]['animal_id']
    response1 = requests.post(baseURL + f'/employee/{employee_id}/care/{animal_id}')
    jo2 = json.loads(response1.content)
    assert jo2 == (f"The care taker with ID {employee_id} is taking care of the animal with ID {animal_id} ")

@pytest.fixture(scope='session') #structure to give the API the body parameter new employee id
def build_request_body():
    def _build(new_employee_id):
        return { "new_employee_id": new_employee_id}
    return _build

def test_DeleteEmployee(baseURL, build_request_body, authorization_token):
    response = requests.get(baseURL + "/employees")
    jo = json.loads(response.content)
    employee_id = jo[0]['employee_id'] #who will be deleted
    animal = jo[0]['animals'][0]
    animal_name = animal['common_name']
        #create a new employee who will receive the animals from the employee who will be deleted
    requests.post(baseURL + "/employee", {"name": "Tom", "address": "Vienna"})
    response1 = requests.get(baseURL + "/employees")
    jo1 = json.loads(response1.content)
    new_employee_id = jo1[-1]['employee_id']

    api_request = build_request_body(new_employee_id= new_employee_id)
    url = f"{baseURL}/employee/{employee_id}"
    header = {"Authorization": authorization_token}
    response2 = requests.delete(url=url, data=api_request, headers=header)

    jo2 = json.loads(response2.content)
    assert jo2 == f"Employee (care taker) with ID {employee_id} was removed. The supervision of the animals was transfered to another employee with ID {new_employee_id} "

    response3 = requests.get(baseURL + "/employees")
    jo3 = json.loads(response3.content)

    assert animal['common_name'] == jo3[-1]['animals'][0]['common_name'] #checking that the animal is been taking care of the new employee
    response4 = requests.get(baseURL+ f"/employee/{new_employee_id}/care/animals")
    jo4 = json.loads(response4.content)
    assert jo4 == f"The employee with ID {new_employee_id} is taking care of the following animals: [{animal_name}] "

def test_StatsEmployee(baseURL, zooWithOneEmployee):
    #Testing when there are 2 animals taken care of one employee and another employee without animals in charge
    jo = json.loads(zooWithOneEmployee)
    response = requests.get(baseURL + "/employees")
    jo1 = json.loads(response.content)
    employee_id = jo1[-1]['employee_id']
    response1 = requests.get(baseURL + f"/animals")
    jo2 = json.loads(response1.content)
    animal_id = jo2[0]['animal_id']
    animal_id2 = jo2[1]['animal_id']
        #Add 2 animals to the animals list of 1 employee:
    requests.post(baseURL + f'/employee/{employee_id}/care/{animal_id}')
    requests.post(baseURL + f'/employee/{employee_id}/care/{animal_id2}')
    response2 = requests.get(baseURL + f'/employees')
    jo3 = json.loads(response2.content)
    assert len(jo3[0]['animals']) == 1 #the first employee on the list has already one animal in his list
    assert len(jo3[1]['animals']) == 2
    response4 = requests.get(baseURL + f"/employee/stats")
    jo4 = json.loads(response4.content)
    assert jo4 == f"The statistics about the employees are: The maximum number of animals under the supervision of a single employee is: 2.  The minimum number of animals under the supervision of a single employee is: 1. The average of animals under the supervision of a single employee is: 1.5 "
