ERROR_TYPE_DATABASE = {
    "arithmetic_error": {
        "description": "기본 연산 실수 (덧셈, 뺄셈, 곱셈, 나눗셈)",
        "examples": ["2+3=6", "15÷3=6"],
        "applicable_grades": [1, 2, 3, 4, 5, 6]
    },
    "distributive_law_error": {
        "description": "분배법칙 미적용 또는 잘못된 적용",
        "examples": ["2(x+3) = 2x+3"],
        "applicable_grades": [5, 6]
    },
    "fraction_addition_error": {
        "description": "분수 덧셈에서 분모끼리 더하기",
        "examples": ["1/2 + 1/3 = 2/5"],
        "applicable_grades": [3, 4, 5, 6]
    },
    "condition_omission": {
        "description": "문제 조건 누락",
        "examples": ["'3의 배수만' 조건 무시"],
        "applicable_grades": [3, 4, 5, 6]
    },
    "formula_confusion": {
        "description": "공식 혼동 (넓이↔둘레 등)",
        "examples": ["직사각형 넓이를 2(가로+세로)로 계산"],
        "applicable_grades": [4, 5, 6]
    },
    "sign_error": {
        "description": "부호 실수",
        "examples": ["-3 + 5 = -8"],
        "applicable_grades": [1, 2, 3, 4, 5, 6]
    },
    "unit_conversion_error": {
        "description": "단위 변환 오류",
        "examples": ["1km = 100m"],
        "applicable_grades": [2, 3, 4, 5, 6]
    },
    "logic_leap": {
        "description": "논리적 단계 생략",
        "examples": ["중간 계산 없이 바로 답으로"],
        "applicable_grades": [5, 6]
    }
}
