package qa.demo.tests;

import com.github.javafaker.Faker;
import org.junit.jupiter.api.Test;

import java.util.Locale;


public class ValidationTests extends TestBase {

    Faker faker = new Faker(new Locale("en"));

    String firstName = faker.name().firstName(),
            lastName = faker.name().lastName(),
            email = faker.internet().emailAddress(),
            phoneNumber = faker.phoneNumber().subscriberNumber(10),
            address = faker.address().fullAddress(),
            state = "Haryana",
            city = "Karnal";


    @Test
    void fillFormTest() {

        //fill form
        registrationPage.openPage()
                .typeFirstName(firstName)
                .typeLastName(lastName)
                .typeEmail(email)
                .chooseGender()
                .typeNumber(phoneNumber)
                .setDate("20", "March", "1996")
                .typeSubject("M", "Maths")
                .chooseHobbies("Sports")
                .uploadImage("src/test/resources/img/img.png")
                .typeAddress(address)
                .chooseState(state)
                .chooseCity(city)
                .submit();

        //check results
        registrationPage.checkResultsValue("Student Name", firstName + " " + lastName)
                .checkResultsValue("Student Email", email)
                .checkResultsValue("Gender", "Male")
                .checkResultsValue("Mobile", phoneNumber)
                .checkResultsValue("Date of Birth", "20 March,1996")
                .checkResultsValue("Subjects", "Maths")
                .checkResultsValue("Hobbies", "Sports")
                .checkResultsValue("Picture", "img.png")
                .checkResultsValue("Address", address)
                .checkResultsValue("State and City", state + " " + city);

    }

}
