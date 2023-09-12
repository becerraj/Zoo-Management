from flask import Flask, jsonify
from flask_restx import Api, reqparse, Resource
from zoo_json_utils import ZooJsonEncoder 
from zoo import Zoo, CareTaker, Enclosure, Animal
import datetime

my_zoo = Zoo()

zooma_app = Flask(__name__)
# need to extend this class for custom objects, so that they can be jsonified
zooma_app.json_encoder = ZooJsonEncoder 
zooma_api = Api(zooma_app)

animal_parser = reqparse.RequestParser()
animal_parser.add_argument('species', type=str, required=True, help='The scientific name of the animal, e,g. Panthera tigris')
animal_parser.add_argument('name', type=str, required=True, help='The common name of the animal, e.g., Tiger')
animal_parser.add_argument('age', type=int, required=True, help='The age of the animal, e.g., 12')

    #I need this parameter for home method:
enclosure_id_parser= reqparse.RequestParser()
enclosure_id_parser.add_argument('enclosure_id', type=str, required=True, help='The ID of the enclosure, e.g., ad639e64-282e-4056-b7e3-bfb7094f8eb9 ')

    #I need this parameter for the delete employee method:
new_employee_id_parser= reqparse.RequestParser()
new_employee_id_parser.add_argument('new_employee_id', type=str, required=True, help='The ID of the employee who will take care of the animals from the old employee, e.g., cb639e64-282e-4056-b7e3-bfb7094f8eb9 ')

    #I need this parameter for the delete enclosure method:
new_enclosure_id_parser= reqparse.RequestParser()
new_enclosure_id_parser.add_argument('new_enclosure_id', type=str, required=True, help='The ID of the enclosure which will hold the animals that were in the old enclosure, e.g., cb639e64-282e-4056-b7e3-bfb7094f8eb9 ')


animal_id_parser= reqparse.RequestParser()
animal_id_parser.add_argument('animal_id', type=str, required=True, help='The ID of the animal, e.g., cb639e64-282e-')

enclosure_parser = reqparse.RequestParser()
enclosure_parser.add_argument('name', type=str, required=True, help='The name of the enclosure, e.g., cage')
enclosure_parser.add_argument('area', type=str, required=True, help='The area of the enclosure, e.g., 50')

employee_parser = reqparse.RequestParser()
employee_parser.add_argument('name', type=str, required=True, help='The name of the employee, e.g., Tom')
employee_parser.add_argument('address', type=str, required=True, help='The address of the employee, e.g., Krems')


@zooma_api.route('/animal')
class AddAnimalAPI(Resource):
    @zooma_api.doc(parser=animal_parser)
    def post(self):
        # get the post parameters 
        args = animal_parser.parse_args()
        name = args['name']
        species = args['species']
        age = args['age']
        # create a new animal object 
        new_animal = Animal(species, name, age) 
        #add the animal to the zoo
        my_zoo.addAnimal(new_animal) 
        return jsonify(new_animal)


@zooma_api.route('/animal/<animal_id>')
class Animal_ID(Resource):
     def get(self, animal_id):
        search_result = my_zoo.getAnimal(animal_id)
        return jsonify(search_result) # this is automatically jsonified by flask-restx
    
     def delete(self, animal_id):
        targeted_animal = my_zoo.getAnimal(animal_id)
        if not targeted_animal: 
            return jsonify(f"Animal with ID {animal_id} was not found")
        my_zoo.removeAnimal(targeted_animal)
        return jsonify(f"Animal with ID {animal_id} was removed") 

@zooma_api.route('/animals')
class AllAnimals(Resource):
     def get(self):
        return jsonify(my_zoo.animals)
     
@zooma_api.route('/animals/<animal_id>/feed')
class FeedAnimal(Resource):
     def post(self, animal_id):
        targeted_animal = my_zoo.getAnimal(animal_id)
        if not targeted_animal: 
            return jsonify(f"Animal with ID {animal_id} was not found") 
        targeted_animal.feed()
        return jsonify(f"{targeted_animal} was fed")

@zooma_api.route('/animals/<animal_id>/vet')
class VetAnimal(Resource):
    def post(self, animal_id):
        targeted_animal = my_zoo.getAnimal(animal_id)
        if not targeted_animal:
            return jsonify(f"Animal with ID {animal_id} was not found")
        targeted_animal.vet()
        return jsonify(f"Animal with ID {animal_id} had a medical checkup")

@zooma_api.route('/animals/<animal_id>/home')
class HomeAnimal(Resource):
    @zooma_api.doc(parser=enclosure_id_parser) #add the query parameter enclosure id. It is not part of the path
    def post(self, animal_id):
        targeted_animal = my_zoo.getAnimal(animal_id)
        if not targeted_animal:
            return jsonify(f"Animal with ID {animal_id} was not found")
        args = enclosure_id_parser.parse_args()
        enclosure_id = args['enclosure_id']
        targeted_enclosure= my_zoo.getEnclosure(enclosure_id)
        if not targeted_enclosure:
            return jsonify(f"Enclosure with ID {enclosure_id} was not found")

        targeted_animal.home(targeted_enclosure, my_zoo)
        return jsonify(f"Animal called {targeted_animal} with ID {animal_id} is living in {targeted_enclosure} which ID is {enclosure_id}")

@zooma_api.route('/animals/birth')
class BirthAnimal(Resource):
    @zooma_api.doc(parser=animal_id_parser) #I need to add the parameter animal id to indicate which animal is giving birth
    def post(self):
        args = animal_id_parser.parse_args()
        mother_id = args['animal_id']
        targeted_mother = my_zoo.getAnimal(mother_id)
        if not targeted_mother:
            return jsonify(f"Mother with ID {mother_id} was not found")
        if (str(targeted_mother.enclosure) == ""):
            return jsonify("It is necessary to assign an enclosure to the mother (home method)")

        baby= targeted_mother.birth(my_zoo) #birth method returns the new animal object which is the child
        my_zoo.addAnimal(baby)
        return jsonify(f"Animal with ID {mother_id} has given birth")

@zooma_api.route('/animals/death')
class DeathAnimal(Resource):
    @zooma_api.doc(parser=animal_id_parser) #indicate which animal has died
    def post(self):
        args = animal_id_parser.parse_args()
        animal_id = args['animal_id']
        targeted_animal = my_zoo.getAnimal(animal_id)
        if not targeted_animal:
            return jsonify(f"Animal with ID {animal_id} was not found")
        my_zoo.death(targeted_animal)
        return jsonify(f"Animal with ID {animal_id} is dead")


@zooma_api.route('/animals/stats')
class StatsAnimals(Resource): 
    def get(self):
        #conditions to avoid the program to crash:
        if (len(my_zoo.animals)==0):
            return jsonify("It is necessary to add animal/s to the zoo")
        if (len(my_zoo.enclosures)==0):
            return jsonify("It is necessary to add enclosure/s to the zoo")
        for i in range(0, (len(my_zoo.animals)-1)):
            if (str(my_zoo.animals[i].enclosure) ==""):
                return jsonify("It is necessary to assign an enclosure to every animal")

        animal_stats = my_zoo.stats()
        return jsonify(f"Statistics about the animals in the zoo are: "
                       f"Total number of animal per species is: {animal_stats[0]}. "
                       f"The number of enclosures with animals from multiple species is: {animal_stats[1]}. "
                       f"The average number of animals per enclosure is: {animal_stats[2]}. "
                       f"The available space in each enclosure for every animal in it is:{animal_stats[3]}")

@zooma_api.route('/tasks/cleaning')
class Cleaning(Resource):
    def get(self):
        my_zoo.cleaning()
        #loop through lists of the attributes of the zoo:
        for enclosure in my_zoo.enclosures:
            for dates in my_zoo.cleaning_dates:
                for responsible in my_zoo.responsibles_clean:
                    return jsonify("The next date for cleaning the enclosure: ", enclosure, "is: ", dates, ". And the person responsible for the cleaning plan is:  ", responsible)

@zooma_api.route('/tasks/medical')
class MedicalPlan(Resource):
    def get(self):
        my_zoo.medical()
        for animal in my_zoo.animals:
            for dates in my_zoo.medical_dates:
                return jsonify("The next date for checking the animal: ", animal.common_name, "is: ", dates)
@zooma_api.route('/tasks/medicaldates') #I made this method in order to test the API
class MedicalDates(Resource):
    def get(self):
        return jsonify(my_zoo.medical_dates)

@zooma_api.route('/tasks/feeding')
class FeedingPlan(Resource):
    def get(self):
        no_caretaker=0
        for animal in my_zoo.animals:
            if (animal.care_taker==''):
                no_caretaker+=1
        if (no_caretaker>0):
            return "It is necessary to assign a care taker to every animal"
        else:
            my_zoo.feeding()
            for animal in my_zoo.animals:
                for dates in my_zoo.feeding_dates:
                    for caretaker in my_zoo.responsibles_feed:
                        return jsonify(f"The next time for feeding the animal: {animal} is: ", dates, ". And the person responsible for the feeding is: ", caretaker)


############################################################### Enclosure

@zooma_api.route('/enclosure')
class AddEnclosureAPI(Resource):
    @zooma_api.doc(parser=enclosure_parser)
    def post(self):
        # get the post parameters
        args = enclosure_parser.parse_args()
        name = args['name']
        area = args['area']
        new_enclosure = Enclosure(name, area)
        my_zoo.addEnclosure(new_enclosure)
        return jsonify(new_enclosure)

@zooma_api.route('/enclosures')
class AllEnclosures(Resource):
     def get(self):
        return jsonify(my_zoo.enclosures)

@zooma_api.route('/<enclosure_id>/clean')
class CleanEnclosure(Resource):
    def post(self, enclosure_id):
        targeted_enclosure = my_zoo.getEnclosure(enclosure_id)
        if not targeted_enclosure:
            return jsonify(f"Enclosure with ID {enclosure_id} was not found")
        targeted_enclosure.clean()
        return jsonify(f"Enclosure with ID {enclosure_id} has been cleaned")

@zooma_api.route('/enclosures/<enclosure_id>/animals')
class getAnimalsInEnclosure(Resource):
    def get(self, enclosure_id):
        targeted_enclosure = my_zoo.getEnclosure(enclosure_id)
        if not targeted_enclosure:
            return jsonify(f"Enclosure with ID {enclosure_id} was not found")

        animals_enclosure = targeted_enclosure.infoAnimalsEncl()
        return jsonify(f"In the enclosure with ID {enclosure_id} are living the following animals: {animals_enclosure} ")

@zooma_api.route('/enclosure/<enclosure_id>')
class DeleteEnclosure(Resource):
    @zooma_api.doc(parser=new_enclosure_id_parser)
    def delete(self, enclosure_id):
        #I need to create a parameter where the user can indicate to which enclosure the animals will be moved to
        args = new_enclosure_id_parser.parse_args()
        new_enclosure_id = args['new_enclosure_id']
        targeted_old_enclosure = my_zoo.getEnclosure(enclosure_id)
        targeted_new_enclosure = my_zoo.getEnclosure(new_enclosure_id)
        if not targeted_old_enclosure:
            return jsonify(f"Enclosure with ID {enclosure_id} was not found")
        if not targeted_new_enclosure:
            return jsonify(f"Enclosure with ID {new_enclosure_id} was not found")
        my_zoo.deleteEncl(targeted_old_enclosure, targeted_new_enclosure)
        return jsonify(f"Enclosure with ID {enclosure_id} was removed. It's animals were transfered to enclosure with ID {new_enclosure_id}")

################################################################# Employee
@zooma_api.route('/employee')
class AddEmployeeAPI(Resource):
    @zooma_api.doc(parser=employee_parser)
    def post(self):
        # get the post parameters
        args = employee_parser.parse_args()
        name = args['name']
        address = args['address']
        # create a new employee object
        new_employee = CareTaker(name, address)
        #add the employee to the zoo
        my_zoo.addCareTaker(new_employee)
        return jsonify(new_employee)

@zooma_api.route('/employees') #I have created this method to make the testing simpler
class AllEmployees(Resource):
     def get(self):
        return jsonify(my_zoo.caretakers)

@zooma_api.route('/employee/<employee_id>/care/<animal_id>')
class AssignAnimaltoEmployee(Resource):
    def post(self, employee_id, animal_id):
        targeted_employee = my_zoo.getEmployee(employee_id)
        targeted_animal = my_zoo.getAnimal(animal_id)
        if not targeted_employee:
            return jsonify(f"Employee with ID {employee_id} was not found")
        if not targeted_animal:
            return jsonify(f"Animal with ID {animal_id} was not found")
        targeted_employee.takesCareof(targeted_animal, my_zoo)
        return jsonify(f"The care taker with ID {employee_id} is taking care of the animal with ID {animal_id} ")

@zooma_api.route('/employee/<employee_id>/care/animals')
class getAnimalsofEmployee(Resource):
    def get(self, employee_id):
        targeted_employee = my_zoo.getEmployee(employee_id)
        if not targeted_employee:
            return jsonify(f"Employee with ID {employee_id} was not found")
        animals_employee = targeted_employee.animalsSupervised()
        return jsonify(f"The employee with ID {employee_id} is taking care of the following animals: {animals_employee} ")

@zooma_api.route('/employee/stats')
class getStatsEmployee(Resource): 
    def get(self):
        stats_employee = my_zoo.statsEmployee()
        return jsonify(f"The statistics about the employees are: "
                       f"The maximum number of animals under the supervision of a single employee is: {stats_employee[0]}.  "           
                       f"The minimum number of animals under the supervision of a single employee is: {stats_employee[1]}. "
                       f"The average of animals under the supervision of a single employee is: {stats_employee[2]} ")

@zooma_api.route('/employee/<employee_id>')
class Employee_ID(Resource):
    def get(self, employee_id):
        search_result = my_zoo.getEmployee(employee_id)
        return jsonify(search_result)

    @zooma_api.doc(parser=new_employee_id_parser)
    def delete(self, employee_id):
        #I need to add a parameter to indicate to which employee the animals will be assigned to
        args = new_employee_id_parser.parse_args()
        new_employee_id = args['new_employee_id']
        targeted_old_employee = my_zoo.getEmployee(employee_id)
        targeted_new_employee = my_zoo.getEmployee(new_employee_id)
        if not targeted_old_employee:
            return jsonify(f"Employee with ID {employee_id} was not found")
        if not targeted_new_employee:
            return jsonify(f"Employee with ID {new_employee_id} was not found")
        my_zoo.deleteEmpl(targeted_old_employee, targeted_new_employee)
        return jsonify(f"Employee (care taker) with ID {employee_id} was removed. The supervision of the animals was transfered to another employee with ID {new_employee_id} ")


if __name__ == '__main__':
    zooma_app.run(debug = True, port = 7890)
