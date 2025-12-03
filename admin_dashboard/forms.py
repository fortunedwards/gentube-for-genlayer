from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, URL, Length, Optional
import validators

class VideoForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(message="Title is required"),
        Length(min=1, max=200, message="Title must be between 1 and 200 characters")
    ])
    url = StringField('URL', validators=[
        DataRequired(message="URL is required"),
        Length(max=500, message="URL must be less than 500 characters")
    ])
    speaker = StringField('Speaker', validators=[
        DataRequired(message="Speaker is required"),
        Length(min=1, max=100, message="Speaker must be between 1 and 100 characters")
    ])
    tags = StringField('Tags', validators=[
        Optional(),
        Length(max=500, message="Tags must be less than 500 characters")
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=2000, message="Description must be less than 2000 characters")
    ])
    submit = SubmitField('Save Video')

    def validate_url(self, field):
        if not validators.url(field.data):
            raise validators.ValidationError('Invalid URL format')

class BulkImportForm(FlaskForm):
    file = FileField('JSON File', validators=[
        DataRequired(message="Please select a file"),
        FileAllowed(['json'], 'Only JSON files are allowed')
    ])
    submit = SubmitField('Import Videos')