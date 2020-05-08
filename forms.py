from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, TextAreaField
from wtforms.validators import InputRequired, Length

#User form to register or login
class UserForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

class SearchForm(FlaskForm):    #type in the ISBN number of a book, the title of a book, or the author of a book
    #parameter = RadioField('Label', choices=[('1','ISBN'), ('2','Title'), ('3','Author')], validators=[InputRequired()])
    searchinput = StringField('Insert the search term', validators=[InputRequired()])
    #title = StringField('Title', validators=[Length(max=50)])
    #author = StringField('Author', validators=[Length(max=50)])

class ReviewForm(FlaskForm):
    rating = RadioField('Label', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')], validators=[InputRequired()])
    review = TextAreaField(validators=[InputRequired(), Length(min=4, max=500)], render_kw={"rows": 10, "cols": 120})