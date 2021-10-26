package qa.demo;

import com.codeborne.selenide.Configuration;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;


import java.io.File;

import static com.codeborne.selenide.Condition.image;
import static com.codeborne.selenide.Condition.text;
import static com.codeborne.selenide.Selectors.byText;
import static com.codeborne.selenide.Selenide.*;


public class ValidationTests {

    @BeforeAll
    static void browserSetting(){
        Configuration.startMaximized = true;
    }

    @Test
    void fillFormTest(){
        open("https://demoqa.com/automation-practice-form");

        $("#firstName").setValue("Some first name");

        $("#lastName").setValue("Some last name");

        $("#userEmail").setValue("sample@gmail.com");

        $(".custom-control-label").click();

        $("#userNumber").setValue("7777777777");

        $("#dateOfBirthInput").click();
        $(".react-datepicker__month-select").selectOptionByValue("2");
        $(".react-datepicker__year-select").selectOptionByValue("1996");
        $$(".react-datepicker__day").find(text("20")).click();

        $("#subjectsInput").click();
        $("#subjectsInput").setValue("M");
        $(byText("Maths")).click();

        $("[for='hobbies-checkbox-1']").click();

        File img = new File("src/test/resources/img.png");
        $("#uploadPicture").uploadFile(img);


        $("#currentAddress").setValue("some adress");


        $("#submit").click();

        $("#submit").click();










    }

}
