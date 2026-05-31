Feature: Управління прийомами
  As a user of the system
  I want to ensure appointment flows work
  So that data is saved correctly

  Scenario: Створення прийому з роботою, матеріалами та ліками
    Given a running API at "http://localhost:8000"
    When I create a patient named "Пацієнт" with dob "2003-12-01"
    And I create a doctor named "Лікар" specialization "Терапевт"
    And I create work category "Огляд" with price 150.00
    And I create material category "Бинт" with cost_price 5.0
    And I create medicine category "Спрей" with cost_price 20.0
    And I create procedure category "Процедура 1" with cost_price 10.0
    And I create a request for the patient with doctor
    And I create an appointment for that request
    And I add a work to the appointment using the work category
    And I add 2 materials to the work using the material category
    And I add 1 medicine to the work using the medicine category
    Then the appointment detail should contain at least 1 work
    And the work should have materials count 2 and medicines count 1