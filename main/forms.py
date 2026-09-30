from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Review, Product


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

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'seller', 'icon']
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'price': 'Цена',
            'category': 'Категория',
            'seller': 'Продавец',
            'icon': 'Изображение',
        }

    def clean_icon(self):
        icon = self.cleaned_data.get('icon')
        if icon and icon.size > 2 * 1024 * 1024:
            raise forms.ValidationError(
                'Размер изображения не должен превышать 2 МБ.'
            )
        return icon


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Имя пользователя"
        self.fields['email'].label = "Ваш Email"
        self.fields['password1'].label = "Пароль"
        self.fields['password2'].label = "Подтверждение пароля"

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email