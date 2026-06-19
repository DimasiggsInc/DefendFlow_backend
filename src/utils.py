from docxtpl import DocxTemplate


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def generate_protocol_from_template(data: dict, template_path="../static/template.docx", output_path="./"):
    doc = DocxTemplate(template_path)
    
    avg_client = sum(c['score'] for c in data['clients']) / len(data['clients'])
    avg_expert = sum(e['score'] for e in data['experts']) / len(data['experts'])
    final_score = round(0.5 * avg_client + 0.5 * avg_expert, 2)
    
    context = {
        'topic': data['topic'],
        'students': ', '.join(data['students']),
        'groups': ', '.join(data['groups']),
        'clients': data['clients'],
        'experts': data['experts'],
        'avg_expert': round(avg_expert, 2),
        'avg_client': round(avg_client, 2),
        'final_score': final_score,
        'questions': "\n".join(data['questions']),
        'summary': data.get('summary', ''),
        'admin_name': data['admin_name'],
        'date': data['date']
    }
    
    doc.render(context)
    doc.save(output_path)
    print(f"Документ сформирован по шаблону: {output_path}")


def get_user_full_name(user_or_profile) -> str:
    """
    Получить полное имя.
    Работает с User, Student, Expert, Admin.
    """
    obj = user_or_profile
    
    if not obj:
        return "Неизвестно"
    
    # 1. Если у объекта есть метод get_full_name (User)
    if hasattr(obj, 'get_full_name'):
        full_name = obj.get_full_name()
        if full_name:
            return full_name
    
    # 2. Если это User напрямую - собираем из частей
    if hasattr(obj, 'last_name') or hasattr(obj, 'first_name'):
        parts = []
        if hasattr(obj, 'last_name') and obj.last_name:
            parts.append(obj.last_name)
        if hasattr(obj, 'first_name') and obj.first_name:
            parts.append(obj.first_name)
        if hasattr(obj, 'middle_name') and obj.middle_name:  # 🔥 middle_name, не patronymic
            parts.append(obj.middle_name)
        
        if parts:
            return ' '.join(parts)
    
    # 3. Если это Student/Expert/Admin - получаем имя через user
    if hasattr(obj, 'user') and obj.user:
        return get_user_full_name(obj.user)
    
    # 4. Fallback на email
    if hasattr(obj, 'email') and obj.email:
        return obj.email
    
    return "Неизвестно"




if __name__ == "__main__":
    payload = {
        "topic": "Основы построения гетерогенной информационной инфраструктуры предприятия. Уровень 1(1).",
        "students": [
            "Аккузин Роман Павлович", 
            "Виноградов Егор Романович", 
            "Воронов Михаил Денисович", 
            "Губайдулин Искандар Эдуардович", 
            "Мусихин Егор Сергеевич"
        ],
        "groups": ["РИ-241002", "РИ-241003"],
        "clients": [
            {"name": "Партов Фарход Расулжонович", "score": 100},
            {"name": "Партов Фарход Расулжонович", "score": 10}
        ],
        "experts": [
            {"name": "Шпаковская Злата Михайловна, системный инженер, УЦСБ", "score": 70},
            {"name": "Востриков Николай Владимирович, системный инженер 1 категории, УЦСБ", "score": 70},
            {"name": "Кужбанова Елена Александровна, ст. преподаватель ИРИТ-РТФ", "score": 70}
        ],
        "questions": [
            "Какова актуальность темы и практическая значимость достигнутых результатов?",
            "Для чего этот стенд был разработан? для каких целей?"
        ],
        "summary": "Проект соответствует требованиям, стенд работоспособен.",
        "admin_name": "А.В. Манжосов",
        "date": "22.05.2026" # Текущая дата
    }

    generate_protocol_from_template(payload, "../static/template.docx")
