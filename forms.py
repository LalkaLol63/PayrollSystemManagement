from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    DecimalField,
    DateField,
    SelectField,
    IntegerField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    NumberRange,
)


class LoginForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class EmployeeForm(FlaskForm):
    marital_status_choices = ["Single", "Married"]
    gender_choices = ["Male", "Female"]

    department_id = IntegerField("Department Id")
    name = StringField("Name", validators=[DataRequired()])
    monthly_salary = DecimalField(
        "Month salary",
        validators=[NumberRange(min=0.0, message="Salary cannot be less than zero!")],
    )
    date_of_birth = DateField("Date of birth", validators=[DataRequired()])
    date_of_employment = DateField("Date of employment", validators=[DataRequired()])
    marital_status = SelectField(
        "Marital status", choices=marital_status_choices, validators=[DataRequired()]
    )
    gender = SelectField("Gender", choices=gender_choices, validators=[DataRequired()])
    number_of_children = IntegerField("Number of children")
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Add employee")


class SickLeaveForm(FlaskForm):
    employee_id = IntegerField("Employee Id", validators=[DataRequired()])
    start_date = DateField("Start date:", validators=[DataRequired()])
    end_date = DateField("End date:", validators=[DataRequired()])

    submit = SubmitField("Add sick leave")

    def validate_end_date(form, field):
        start_date = form.start_date.data
        end_date = field.data

        if end_date < start_date:
            raise ValidationError(
                "End date must be greater than or equal to start date."
            )
