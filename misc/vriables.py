MONEY_TYPES = [
    ('money', 'money'),
    ('bottle', 'bottle'),
    ('donat', 'donat'),
    ('detail', 'detail')
]

STUFF_TYPES = [
    ('shirts', 'shirts'),
    ('shoes', 'shoes'),
    ('pants', 'pants'),
    ('jacket', 'jacket'),
    ('donat_stuff', 'donat_stuff')
]

NUMBER_TYPES = [
    ('regular', 'regular'),
    ('name', 'name')
]

BOMJ_TIMES_CHAT_ID = '@BomjSimTimes'
BOMJ_CHAT_ID = '@BomjSim'

SMILE_MONEY_TYPE = {
    'money': '💰',
    'bottle': '🍾',
    'donat': '💵',
    'keyses': "🗃",
    'exp': '📊',
    'rating': '⭐️',
    'lvl': '📊'
}

MEDAL_TYPES = {
    1: '🥇',
    2: '🥈',
    3: "🥉",
    4: '🎖',
    5: '🎖'
}

SORT_TRASH_WORK_KEYBOARD = {'Металл': 1, 'Стекло': 2, 'Пластик': 3}

CONDUCTOR_WORK_KEYBOARD = {'Пропустить': 1, "Выгнать": 2}

ORDER_PICKER_ORDERS = {'Принять': 'accept_new_order', 'Отклонить': 'cancel_new_order'}
ORDER_PICKER_TYPES_KEYBOARD = {'Фрукты': 1, 'Напитки': 2, "Рыба": 3, "Выпечка": 4, "Молочка": 5, "Мясо": 6, "Овощи": 7,
                               'Завершить сборку заказа': 'order_finish'}

COLLECT_BOTTLE_KEYBOARD = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6}

# Словарь содержит призы для победителей в махачах ( верхний уровень - позиция банды, нижний - позиция конкретного игрока )
MAXA_FINISH = {
    1: {
        1: {
            'money': 5_000_000,
            'bottle': 500_000,
            'exp': 50
        },
        2: {
            'money': 3_000_000,
            'bottle': 250_000,
            'exp': 25
        },
        3: {
            'money': 1_000_000,
            'bottle': 100_000,
            'exp': 15
        }
    },
    2: {
        1: {
            'money': 500_000,
            'bottle': 50_000,
            'exp': 10
        },
        2: {
            'money': 500_000,
            'bottle': 50_000,
            'exp': 10
        },
        3: {
            'money': 500_000,
            'bottle': 50_000,
            'exp': 10
        }
    },
    3: {
        1:
            {
                'money': 500_000,
                'bottle': 50_000,
                'exp': 10
            },
        2: {
            'money': 500_000,
            'bottle': 50_000,
            'exp': 10
        },
        3: {
            'money': 500_000,
            'bottle': 50_000,
            'exp': 10
        }
    }
}


COUNT_BANDA_RATING = {
    1: 5,
    2: 3,
    3: 1
}


PRISE_FISHING_EVENT = {
    1: {
        'money': 500_000,
        'bottle': 100_000,
        'exp': 25
    },
    2: {
        'money': 250_000,
        'bottle': 50_000,
        'exp': 15
    },
    3: {
        'money': 100_000,
        'bottle': 20_000,
        'exp': 5
    }
}