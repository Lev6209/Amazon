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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget.initial_text = 'Текущее'
        self.fields['icon'].widget.input_text = 'Заменить на'
        self.fields['icon'].widget.clear_checkbox_label = 'Удалить'


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
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с такой почтой уже существует')
        return email


class PriceFilterForm(forms.Form):
    price_min = forms.DecimalField(label='Цена от:', required=False, max_digits=6, decimal_places=2)
    price_max = forms.DecimalField(label='Цена до:', required=False, max_digits=6, decimal_places=2)
    sort = forms.ChoiceField(
        label='Порядок сортировки',
        required=False,
        choices=[
            ('', 'по умолчанию'),
            ('price', 'от дешевых'),
            ('-price', 'от дорогих'),
        ]
    )

    def clean(self):
        cleaned_data = super().clean()

        price_min = cleaned_data.get('price_min')
        price_max = cleaned_data.get('price_max')

        if price_min is not None and price_max is not None:
            if price_min > price_max:
                raise forms.ValidationError(
                    'Цена "от" не может быть больше цены "до"'
                )

        return cleaned_data


class DateFilterForm(forms.Form):
    date_min = forms.DateField(
        label='Начальная дата:',
        required=False,
        input_formats=['%Y-%m-%d', '%d.%m.%Y'],
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    date_max = forms.DateField(
        label='Конечная дата:',
        required=False,
        input_formats=['%Y-%m-%d', '%d.%m.%Y'],
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    contains = forms.CharField(
        label='Содержит:',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Название товара/категории'
        })
    )

    def clean(self):
        cleaned_data = super().clean()

        date_min = cleaned_data.get('date_min')
        date_max = cleaned_data.get('date_max')

        if date_min is not None and date_max is not None:
            if date_min > date_max:
                raise forms.ValidationError(
                    'Дата "от" не может быть позже даты "до"'
                )

        return cleaned_data