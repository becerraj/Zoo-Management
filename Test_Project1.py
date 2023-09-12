import pytest
#Testing without API:
from zoo import Zoo, Animal, Enclosure, CareTaker

#FIXTURES:------------------------------------------------------

@pytest.fixture
def tiger1():
    return Animal("tiger", "ti", 5)
@pytest.fixture
def tiger2():
    return Animal("tiger", "ga", 2)
@pytest.fixture
def fish1():
    return Animal("fish", "nemo", 1)

@pytest.fixture
def my_zoo():
    return Zoo()

@pytest.fixture
def encl1():
    return Enclosure("cage", 25)
@pytest.fixture
def encl2():
    return Enclosure("pool", 40)

@pytest.fixture
def empl1():
    return CareTaker("Sam", "Krems")
@pytest.fixture
def empl2():
    return CareTaker("John", "Argentina")

@pytest.fixture
def zoo_111(my_zoo, tiger1, empl1, zoo_110): #1 animal assigned to 1 enclosure, 1 employee with 1 animal
    my_zoo.addCareTaker(empl1)
    empl1.takesCareof(tiger1, my_zoo)
@pytest.fixture
def zoo_110(my_zoo, tiger1, encl1): #1 animal assigned to 1 enclosure, 0 employees
    my_zoo.addAnimal(tiger1)
    my_zoo.addEnclosure(encl1)
    tiger1.home(encl1, my_zoo)
#----------------------------------------------------------------------
#TESTS:

def test_AddingAnimal(my_zoo, tiger1, tiger2):
    my_zoo.addAnimal(tiger1)
    assert (tiger1 in my_zoo.animals)
    my_zoo.addAnimal(tiger2)
    assert len(my_zoo.animals)==2

def test_removingAnimal(my_zoo, fish1, tiger2):
    my_zoo.addAnimal(fish1)
    my_zoo.removeAnimal(fish1)
    assert (fish1 not in my_zoo.animals)
    my_zoo.addAnimal(tiger2)
    assert len(my_zoo.animals)==1


def test_addingEnclosure(my_zoo, encl1, encl2):
    my_zoo.addEnclosure(encl1)
    assert (encl1 in my_zoo.enclosures)
    my_zoo.addEnclosure(encl2)
    assert len(my_zoo.enclosures) == 2

def test_addingEmployee(my_zoo, empl1, empl2):
    my_zoo.addCareTaker(empl1)
    assert (empl1 in my_zoo.caretakers)
    my_zoo.addCareTaker(empl2)
    assert (len(my_zoo.caretakers) == 2)

def test_deathAnimal(my_zoo, tiger1, encl1, empl1, zoo_111):
    assert (tiger1 in my_zoo.animals)
    assert (tiger1 in encl1.occupants)
    assert (tiger1 in empl1.animals)
    my_zoo.death(tiger1)
    assert (tiger1 not in my_zoo.animals)
    assert (tiger1 not in encl1.occupants)
    assert (tiger1.enclosure != encl1)
    assert (tiger1 not in empl1.animals)
    assert (tiger1.care_taker != empl1)


def test_deletingEnclosure(my_zoo, encl1, tiger1, encl2, zoo_110):
    my_zoo.deleteEncl(encl1, encl2)
    assert (encl1 not in my_zoo.enclosures)
    assert (tiger1 not in encl1.occupants)
    assert (tiger1 in encl2.occupants)
    assert (tiger1.enclosure == encl2.name)

def test_deletingEmployee(my_zoo, empl1, tiger1, empl2, zoo_111):
    my_zoo.deleteEmpl(empl1, empl2)
    assert (empl1 not in my_zoo.caretakers)
    assert (tiger1 not in empl1.animals)
    assert (tiger1 in empl2.animals)
    assert (tiger1.care_taker == empl2.name)

def test_ZooStats1(my_zoo, tiger1, encl1, zoo_110):
    animal_stats = my_zoo.stats()
    assert ( animal_stats[0] == {'tiger': 1} ) #Total number of animals per species
    assert (animal_stats[1] == 0) #number of enclosures with animals from multiple species
    assert (animal_stats[2] == 1.0 ) #average number of animals per enclosure
    assert (animal_stats[3] == {'cage': 25.0} ) #available space in each enclosure for every animal


def test_ZooStats2(my_zoo, encl1, fish1, zoo_110):
    my_zoo.addAnimal(fish1)
    fish1.home(encl1, my_zoo)
    animal_stats = my_zoo.stats()
    assert (animal_stats[0] == {'tiger': 1, 'fish': 1})  # Total number of animals per species
    assert (animal_stats[1] == 1)  # number of enclosures with animals from multiple species
    assert (animal_stats[2] == 2.0)  # average number of animals per enclosure
    assert (animal_stats[3] == {'cage': 12.5})  # available space in each enclosure for every animal


def test_ZooStatsError(my_zoo, tiger1, encl1):
    my_zoo.addAnimal(tiger1)
    my_zoo.addEnclosure(encl1)
    #I dont execute the "home" method
    with pytest.raises(ZeroDivisionError) as ex:
        print(my_zoo.stats())
    # I expect my program to crash when there are no animals in the enclosure, because it would do a division with 0

def test_EmployeeStats(my_zoo, empl1, empl2, tiger2, fish1, zoo_111):
    #2 caretakers and 3 animals (just 2 of them with caretakers):
    my_zoo.addCareTaker(empl2)
    my_zoo.addAnimal(tiger2)
    my_zoo.addAnimal(fish1)
    empl1.takesCareof(tiger2, my_zoo)
    emplstats = my_zoo.statsEmployee()
    assert (emplstats[0] == 2) #maximum number of animals under the supervision of a single employee
    assert (emplstats[1] == 0) #minimum number of animals under the supervision of a single employee
    assert (emplstats[2] == 1.0)#average of animals under the supervision of a single employee

def test_TakingCareOf(my_zoo, empl1, tiger1, empl2, zoo_111):
    assert (tiger1 in empl1.animals)
    assert (tiger1.care_taker == empl1.name)
    #changing caretaker:
    empl2.takesCareof(tiger1, my_zoo)
    assert (tiger1 not in empl1.animals)
    assert (tiger1 in empl2.animals)
    assert (tiger1.care_taker == empl2.name)

def test_feedingAnimal(my_zoo, tiger1):
    my_zoo.addAnimal(tiger1)
    tiger1.feed()
    assert (len(tiger1.feeding_record)==1)
    tiger1.feed()
    assert len(tiger1.feeding_record)==2

def test_VetAnimal(my_zoo, tiger1):
    my_zoo.addAnimal(tiger1)
    tiger1.vet()
    assert (len(tiger1.medical_record)==1)
    tiger1.vet()
    assert (len(tiger1.medical_record) == 2)

def test_AssigningHome1(tiger1, encl1, encl2, zoo_110, my_zoo):
    assert (tiger1 in encl1.occupants)
    assert (tiger1.enclosure == encl1.name)
    #changing enclosure:
    tiger1.home(encl2, my_zoo)
    assert (tiger1 not in encl1.occupants)
    assert (tiger1 in encl2.occupants)
    assert (tiger1.enclosure == encl2.name)

def test_GivingBirth1(my_zoo, tiger1, encl1, encl2, zoo_110):
    baby = tiger1.birth(my_zoo)
    my_zoo.addAnimal(baby)
    assert (len(encl1.occupants) == 2)
    assert (len(my_zoo.animals) == 2)
    assert (my_zoo.animals[-1].common_name == tiger1.common_name)
    assert (my_zoo.animals[-1].species_name == tiger1.species_name)

    #The baby will stay in its initial enclosure no matter if the mother moves to another enclosure
    tiger1.home(encl2, my_zoo)
    assert (len(encl2.occupants) == 1)

def test_GivingBirth2(my_zoo, fish1, encl1):
    my_zoo.addAnimal(fish1)
    my_zoo.addEnclosure(encl1)
    baby= fish1.birth(my_zoo)
    my_zoo.addAnimal(baby)
    #The mother hasnt been assigned a home
    assert baby.enclosure== ""

def test_GivingBirth3(my_zoo, tiger1, encl1, encl2, zoo_110):
    #zoo_110: tiger1 is already living in enclosure1
    baby = tiger1.birth(my_zoo)
    my_zoo.addAnimal(baby)
    #testing the baby having a baby:
    baby2 = baby.birth(my_zoo)
    my_zoo.addAnimal(baby2)
    assert (len(encl1.occupants) == 3) #tiger1, baby and baby2
    assert (len(my_zoo.animals) == 3)
    assert (my_zoo.animals[-1].common_name == tiger1.common_name)
    assert (my_zoo.animals[-1].common_name == baby.common_name)
    assert (my_zoo.animals[-1].species_name == tiger1.species_name)
    assert (my_zoo.animals[-1].species_name == baby.species_name)

def test_CleaningPlan1(my_zoo, tiger1, tiger2, encl1, encl2, empl1, zoo_111):
    #Situation 1: one enclosure already cleaned with animal with caretaker
    encl1.clean()
    my_zoo.cleaning()
    assert (len(encl1.cleaning_record) == 1)
    assert (len(my_zoo.cleaning_dates) == 1)
    assert (len(my_zoo.responsibles_clean) == 1)
    assert (my_zoo.responsibles_clean[-1] == str(empl1))

def test_CleaningPlan2(my_zoo, encl2, tiger2, empl2, zoo_111):
    #Situation 2: 2 enclosures, JUST one of them is already cleaned, both with animals with caretaker
    my_zoo.addEnclosure(encl2)
    my_zoo.addAnimal(tiger2)
    my_zoo.addCareTaker(empl2)
    tiger2.home(encl2, my_zoo)
    empl2.takesCareof(tiger2, my_zoo)

    encl2.clean()
    with pytest.raises(IndexError) as ex:
        print(my_zoo.cleaning())
    # I expect an index error because it is necessary to apply the clean method before creating a cleaning plan
    # The attribute cleaning_record of the enclosure is empty

def test_CleaningPlan3(my_zoo, tiger1, tiger2, encl1, encl2, empl1, zoo_111):
    #Situation 3: 2 enclosures already cleaned, one of them doesnt have animals in it
    my_zoo.addEnclosure(encl2)
    encl1.clean()
    encl2.clean()
    with pytest.raises(IndexError) as ex:
        print(my_zoo.cleaning())
    # I expect an index error because the occupants list of the enclosure 2 is empty

def test_CleaningPlan4(my_zoo, tiger2, encl1, encl2, zoo_111):
    # Situation 4: 2 enclosures, both already cleaned, the first animal in the list of one of the enclosures doesnt have a caretaker
    my_zoo.addAnimal(tiger2)
    my_zoo.addEnclosure(encl2)
    tiger2.home(encl2, my_zoo)
    encl1.clean()
    encl2.clean()
    my_zoo.cleaning()
    assert (len(encl1.cleaning_record) == 1)
    assert (len(my_zoo.cleaning_dates) == 2)
    assert (my_zoo.responsibles_clean[1] =='')
    #There is a blank space where the name of the caretaker should be
    # because when every animal is created its attribute of care_taker is =''

def test_MedicalPlan1(my_zoo, tiger1):
    #Situation 1: one animal who was already taken to the vet
    my_zoo.addAnimal(tiger1)
    tiger1.vet()
    my_zoo.medical()
    assert (len(tiger1.medical_record)==1)
    assert (len(my_zoo.medical_dates)==1)

def test_MedicalPlan2(my_zoo, tiger1):
    #Situation 2: one animal that hasnt been taken to the vet
    my_zoo.addAnimal(tiger1)
    with pytest.raises(IndexError) as ex:
        print(my_zoo.medical())
    #I expect an index error because the attribute medical_records of the animal is empty

def test_MedicalPlan3(my_zoo, tiger1, tiger2, fish1):
    #Situation 3: 3 animals: one went to the vet 2 times and the others just once
    my_zoo.addAnimal(tiger1)
    tiger1.vet()
    tiger1.vet()
    my_zoo.addAnimal(tiger2)
    tiger2.vet()
    my_zoo.addAnimal(fish1)
    fish1.vet()
    my_zoo.medical()
    assert (len(tiger1.medical_record)==2) #Tiger 1 went to the vet 2 times
    assert (len(my_zoo.medical_dates)==3) #There is one date for each animal that has been taken to the vet before

def test_FeedingPlan1(my_zoo, tiger1, tiger2, encl1, encl2, empl1, zoo_111):
    #Situation 1: one animal already fed with caretaker
    tiger1.feed()
    my_zoo.feeding()
    assert (len(tiger1.feeding_record)==1)
    assert (len(my_zoo.feeding_dates)==1)
    assert (len(my_zoo.responsibles_feed) == 1)
    assert (my_zoo.responsibles_feed[-1]== empl1.name)

    #Situation 2:  2 animals, just one of them was fed twice, both have caretakers
    tiger1.feed()
    my_zoo.addAnimal(tiger2)
    empl1.takesCareof(tiger2, my_zoo)
    with pytest.raises(IndexError) as ex:
        print(my_zoo.feeding())
    #It is necessary to apply the feed method before creating a feeding plan

def test_FeedingPlan2(my_zoo, tiger1, tiger2, empl1, zoo_111):
    #Situation 3: 2 animals already fed, one of them doesnt have caretaker
    my_zoo.addAnimal(tiger2)
    tiger1.feed()
    tiger2.feed()
    my_zoo.feeding()
    assert (len(my_zoo.feeding_dates)==2)
    assert (my_zoo.responsibles_feed[1]=='') #tiger 2 doesnt have a caretaker, so as default it is ''

def test_infoAnimalsEncl(my_zoo, tiger2, encl1, zoo_110):
    my_zoo.addAnimal(tiger2)
    tiger2.home(encl1, my_zoo)
    encl1.infoAnimalsEncl()
    assert (len(encl1.occupants)== 2)
    assert (encl1.occupants[0].species_name == 'tiger')

def test_getAllEnclosures(my_zoo, encl1, encl2, tiger2, zoo_110):
    my_zoo.addAnimal(tiger2)
    my_zoo.addEnclosure(encl2)
    tiger2.home(encl1, my_zoo)
    Enclosure.getEnclosures()
    assert (len(my_zoo.enclosures)==2)
    assert (Enclosure.all_enclosures[0].name == 'cage')


