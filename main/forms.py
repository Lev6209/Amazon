from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['username', 'comment', 'stars', 'recommended']
        labels = {
            'username': 'Ваше имя:',
            'comment': 'Ваш комментарий:',
            'stars': 'Ваша оценка:',
            'recommended': 'Рекомендуете ли вы этот товар?'
        }

        error_messages = {
            'username': {
                'required': 'Пожалуйста, введите ваше имя',
            },
        }

        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Сюда введите ваше имя',
            }),
            'comment': forms.Textarea(attrs={
                'rows': '3',
                'placeholder': 'Поделитесь вашими впечатлениями',
            }),
            'stars': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'style': 'width: 25px'
            }),
        }

    def clean_stars(self):
        stars = self.cleaned_data['stars']
        if stars < 1 or stars > 5:
            raise forms.ValidationError('Оцените пожалуйста товар по пятибалльной шкале')
        return stars

    def clean_username(self):
        username = self.cleaned_data['username']
        if not username.strip():
            raise forms.ValidationError('Это поле обязательно для заполнения')
        return username