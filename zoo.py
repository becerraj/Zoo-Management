import copy
import uuid
import datetime

class Zoo:
    def __init__(self):
        self.animals = []
        self.animal_p_species = {}  # key= specie, value = number of animals of that specie
        self.enclosures = [] #store all the enclosures in the zoo
        self.caretakers = []
        self.area_animal_enclosure = {} #key: enclosure, value= available space per animal
        self.lengths = [] #it stores the lengths of all the animal lists that every employee is responsible for
        self.cleaning_dates = [] #stores the dates calculates by the cleaning plan
        self.responsibles_clean = [] #stores the person responsible for cleaning the enclosure (caretaker of the first occupant of every enclosure)
        self.responsibles_feed = []
        self.medical_dates = []
        self.feeding_dates = []

    def addAnimal(self, animal):
        self.animals.append(animal)
    def removeAnimal(self, animal):
        self.animals.remove(animal)
    def getAnimal(self, animal_id):
        for animal in self.animals:
            if animal.animal_id == animal_id: #detect the animal id given within the animal id of the animals list of the zoo
                return animal

    def addEnclosure(self, enclosure):
        self.enclosures.append(enclosure)
    def getEnclosure(self, enclosure_id):
        for enclosure in self.enclosures:
            if enclosure.enclosure_id == enclosure_id:
                return enclosure

    def addCareTaker(self, employee):
        self.caretakers.append(employee)
    def getEmployee(self, employee_id):
        for employee in self.caretakers:
            if employee.employee_id == employee_id:
                return employee
    def __repr__(self):
        string_ = ""
        for animal in self.animals:
            string_ += "/n" + str(animal)
        return string_

    def stats(self): 
        for animal1 in self.animals:
            num_p_species = 1 #counts the number of animals of one same specie. It starts in 1 because every animal has 1 specie
            for animal2 in self.animals:
                if ((str(animal1.species_name) == str(animal2.species_name)) & (animal1 != animal2)): #Compare species names and ensure that is not the same object of animal
                    num_p_species += 1
            if (str(animal1.species_name) not in self.animal_p_species.keys()): #avoids repeating keys which are the species names
                self.animal_p_species.update({animal1.species_name: num_p_species})
        print("Total number of animal per species is: ", self.animal_p_species)
        # Average of animals per enclosure:
        sum_animals = 0
        count_encl_multiple = 0
        count_encl = 0

        for enclosure in self.enclosures:
            sum_animals += len(enclosure.occupants)  # it is adding the number of animals in each enclosure
            #Available space per animal in it's enclosure
            self.area_animal_enclosure.update({enclosure.name: (int(enclosure.area)/len(enclosure.occupants))})
            for occupant1 in enclosure.occupants:
                for occupant2 in enclosure.occupants:
                    if (str(occupant2.species_name) != str(occupant1.species_name)): #compare species within the animals of one enclosure
                        count_encl = 1
            if count_encl != 0:  # when there are at least 2 different species in one enclosure
                count_encl_multiple += 1
                count_encl = 0  # restart the counter for the next enclosure analysis
        print("The number of enclosures with animals from multiple species is: ", count_encl_multiple)
        av = sum_animals / len(self.enclosures)  # average
        print("The average number of animals per enclosure is: ", av)
        print("The available space in each enclosure for every animal in it is:",self.area_animal_enclosure)
        return self.animal_p_species, count_encl_multiple, av, self.area_animal_enclosure

    def death(self, animal):
        self.removeAnimal(animal)
        if animal.enclosure != "": #to avoid crashing when the dead animal doesnt have an enclosure
            for enclosure in self.enclosures:
                if enclosure.name == animal.enclosure:
                    enclosure.occupants.remove(animal)
        animal.enclosure = ""  # restart the attribute for the home method
        if animal.care_taker != "":
            for caretaker in self.caretakers:
                if caretaker.name == animal.care_taker:
                    caretaker.animals.remove(animal)
        animal.care_taker=""

    def deleteEncl(self, old_enclosure, new_enclosure):
        copy_old = copy.copy(old_enclosure.occupants) #make a copy of the animals that are on the enclosure I will delete
        #I do this copy to make the for loop work, because if I delete and run the loop it will skip objects
        for occupant in copy_old:
            new_enclosure.occupants.append(occupant)
        for occupant in old_enclosure.occupants:
            occupant.enclosure = new_enclosure.name #make a reference to the object enclosure in the attribute of the class animal
            #If I store the object enclosure directly it leads to a circular reference error
        old_enclosure.occupants.clear() #make the animals list of the enclosure empty
        Enclosure.all_enclosures.remove(old_enclosure)
        self.enclosures.remove(old_enclosure)

    def deleteEmpl(self, old_employee, new_employee):
        copy_old = copy.copy(old_employee.animals)
        for animal in copy_old:
            new_employee.animals.append(animal)
        for animal in old_employee.animals:
            animal.care_taker = new_employee.name
        old_employee.animals.clear()
        self.caretakers.remove(old_employee)

    def statsEmployee(self):
        sum_lengths = 0 #stores the lengths of the lists of animals of each care taker
        for employee in self.caretakers:
            self.lengths.append(len(employee.animals)) #store the number of animals that are looked after by every employee
        print("The maximum number of animals under the supervision of a single employee is: ", max(self.lengths))
        print("The minimum number of animals under the supervision of a single employee is: ", min(self.lengths))
        for long in self.lengths:
            sum_lengths += long
        av_supervision = sum_lengths / len(self.lengths) #total of animals that have care takers devided by the quantity of caretakers
        print("The average of animals under the supervision of a single employee is: ", av_supervision)
        return max(self.lengths), min(self.lengths), av_supervision

    def cleaning(self):
        #I have to restart the lists to show every element:
        self.cleaning_dates.clear()
        self.responsibles_clean.clear()
        for enclosure in self.enclosures:
            next_clean = enclosure.cleaning_record[-1] + datetime.timedelta(days=5) #The next clean should be done 5 days after it has been cleaned
            self.cleaning_dates.append(next_clean)
            responsible = str(enclosure.occupants[0].care_taker) #the caretaker of the first animal that has entered to the enclosure is the responsible
            self.responsibles_clean.append(responsible)
            print("The next date for cleaning the enclosure: ", enclosure, "is: ", next_clean, ". And the person responsible for the cleaning plan is:  ", responsible)

    def medical(self):
        self.medical_dates.clear()
        for animal in self.animals:
            next_check = animal.medical_record[-1] + datetime.timedelta(days=10)
            self.medical_dates.append(next_check)
            print("The next date for checking the animal: ", animal, "is: ", next_check)

    def feeding(self):
        self.feeding_dates.clear()
        for animal in self.animals:
            next_feed = animal.feeding_record[-1] + datetime.timedelta(hours=3)
            self.feeding_dates.append(next_feed)
            self.responsibles_feed.append(animal.care_taker)
            print("The next time for feeding the animal: ", animal, "is: ", next_feed, ". And the responsible for the feeding is: ", animal.care_taker)


#############################################################################
class CareTaker:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.animals = [] #stores the animals the care taker will take care of
        self.employee_id = str(uuid.uuid4())

    def __repr__(self):
        return self.name

    def takesCareof(self, animal, zoo):
        self.animals.append(animal)
        if (animal.care_taker != ""): #check if the animal had had a caretaker before
            for caretaker in zoo.caretakers:
                if animal.care_taker == caretaker.name:
                    caretaker.animals.remove(animal) #remove the animal from the lists of animals taken care of the previous care taker
        animal.care_taker = self.name #just make a reference to the care taker in the animal instead of storing the object to avoid circular reference error

    def animalsSupervised(self):
        return self.animals

#######################################################################3
class Animal:
    def __init__(self, species_name, common_name, age):
        self.animal_id = str(uuid.uuid4())
        self.species_name = species_name
        self.common_name = common_name
        self.age = age
        self.feeding_record = []
        self.medical_record = []
        #For the following attributes I will just make a reference about their names in order to detect them within lists in Zoo class.
            #I had had circular reference errors by adding them as objects because both of them have lists with animals objects
        self.enclosure = ""
        self.care_taker = ""


    def feed(self):
        self.feeding_record.append(datetime.datetime.now())

    def vet(self):
        self.medical_record.append(datetime.datetime.now())

    def home(self, enclosure_home, zoo):
        if (self.enclosure != ""): #if the animal had had an enclosure before, I need to remove it from the occupants list from that previous enclosure
            for enclosure in zoo.enclosures:
                if enclosure.name == self.enclosure: #search the previous enclosure within the enclosures of the zoo
                    enclosure.occupants.remove(self)

        self.enclosure = enclosure_home.name
        enclosure_home.occupants.append(self)
        print("The animal ", self.common_name, "is living in: ", self.enclosure)


    def __repr__(self):
        return self.common_name

    def birth(self, zoo):  # mom.birth()
        baby = Animal(str(self.species_name), str(self.common_name), 0) #new object
        for enclosure in zoo.enclosures:
            if enclosure.name == self.enclosure: #search for the enclosure of the mother
                baby.home(enclosure, zoo)
        return baby #make the new object usable from outside the method
       

########################################################################
class Enclosure:
    num_enclosures = 0 #count the enclosures created
    all_enclosures = [] #store every object of this class
    def __init__(self, name, area):
        self.name = name
        self.area= area
        self.enclosure_id = str(uuid.uuid4())
        self.occupants = []
        self.cleaning_record =[]
        Enclosure.num_enclosures += 1
        Enclosure.all_enclosures.append(self)

    def __repr__(self):
        return self.name

    def clean(self):
        actual_date= datetime.datetime.now()
        self.cleaning_record.append(actual_date)
        print("Current date and time of cleanning: ", actual_date.strftime("%Y-%m-%d %H:%M:%S"))

    def infoAnimalsEncl(self):
        print("In this enclosure you can find", len(self.occupants), "animals")
        for occupant in self.occupants:
            print("The name of the animal is: ", occupant.common_name, ", it´s specie is: ", occupant.species_name, "and it has ", occupant.age , "years")
        return self.occupants

    @classmethod
    def getEnclosures(cls):
        print("There are", cls.num_enclosures, "enclosures created")
        for enclosure in cls.all_enclosures: #loop over every enclosure created
            print("In the enclosure ", enclosure.name, "you can find the following animals: ", enclosure.occupants)
        return Enclosure.all_enclosures

