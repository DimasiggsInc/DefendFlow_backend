"""Обработчик проектов."""

import uuid

from fastapi import APIRouter, status


from src.projects.schemas import CuratorSchema, ProjectFullSchemaResponse, ProjectMemberSchema, ProjectLink, ProjectLinkType


router = APIRouter(
    prefix="/project",
    tags=["Project"],
)

# TODO: Добавить проверку прав доступа (только участники проекта, куратор и админ могут видеть информацию о проекте)
# TODO: Добавить обработку ошибок (например, если проект не найден, вернуть 404)

#========GET========#
@router.get("/{project_id}", response_model=ProjectFullSchemaResponse, status_code=status.HTTP_200_OK)
async def get_project_info(project_id: uuid.UUID,): # current_user: dict = Depends(get_current_user)
    """Получить информацию о проекте. (Пока что возвращает заглушку)"""
    curator = CuratorSchema(
        id="123e4567-e89b-12d3-a456-426614174001",
        firstName="Иван",
        lastName="Иванов",
        middleName="Иванович"
    )
    
    member = ProjectMemberSchema(
        id="123e4567-e89b-12d3-a456-426614174002",
        email="mail@example.com",
        firstName="Петр",
        lastName="Петров",
        middleName="Петрович",
        academGroup="РИ-1488_67_42_52",
        roleInTeam="Разработчик"
    )

    link1 = ProjectLink(
        id="123e4567-e89b-12d3-a456-426614174003",
        name="GitHub Repository",
        type=ProjectLinkType.GITHUB,
        url="github.com/example/project",
        description="Репозиторий проекта на GitHub"
    )
    link2 = ProjectLink(
        id="123e4567-e89b-12d3-a456-426614174004",
        name="Figma Design",
        type=ProjectLinkType.DESIGN,
        url="figma.com/example/project-design",
        description="Дизайн проекта в Figma"
    )

    project = ProjectFullSchemaResponse(
        id=project_id,
        name="Пример проекта",
        description="Это пример описания проекта.",
        curator=curator,
        team=[member, member],
        projectLinks=[link1, link2],
    )
    return project

@router.get("/{project_id}/links", response_model=list[ProjectLink], status_code=status.HTTP_200_OK)
async def get_project_links(project_id: uuid.UUID): # current_user: dict = Depends(get_current_user)
    """Получить ссылки на ресурсы проекта. (Пока что возвращает заглушку)"""
    link1 = ProjectLink(
        id="123e4567-e89b-12d3-a456-426614174003",
        name="GitHub Repository",
        type=ProjectLinkType.GITHUB,
        url="github.com/example/project",
        description="Репозиторий проекта на GitHub"
    )
    link2 = ProjectLink(
        id="123e4567-e89b-12d3-a456-426614174004",
        name="Figma Design",
        type=ProjectLinkType.DESIGN,
        url="figma.com/example/project-design",
        description="Дизайн проекта в Figma"
    )
    return [link1, link2]

@router.get("/{project_id}/team", response_model=list[ProjectMemberSchema], status_code=status.HTTP_200_OK)
async def get_project_team(project_id: uuid.UUID): # current_user: dict = Depends(get_current_user)
    """Получить информацию о команде проекта. (Пока что возвращает заглушку)"""
    member = ProjectMemberSchema(
        id="123e4567-e89b-12d3-a456-426614174002",
        email="mail@example.com",
        firstName="Петр",
        lastName="Петров",
        middleName="Петрович",
        academGroup="РИ-1488_67_42_52",
        roleInTeam="Разработчик"
    )
    return [member, member]


#=======POST========#
@router.post("/", response_model=ProjectFullSchemaResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectFullSchemaResponse): # current_user: dict = Depends(get_current_user)
    """Создать новый проект. (Пока что возвращает заглушку)"""
    return project

@router.post("/{project_id}/links", response_model=ProjectLink, status_code=status.HTTP_201_CREATED)
async def add_project_link(project_id: uuid.UUID, link: ProjectLink): # current_user: dict = Depends(get_current_user)
    """Добавить ссылку на ресурс проекта. (Пока что возвращает заглушку)"""
    return link

@router.post("/{project_id}/team", response_model=ProjectMemberSchema, status_code=status.HTTP_201_CREATED)
async def add_project_member(project_id: uuid.UUID, member: ProjectMemberSchema): # current_user: dict = Depends(get_current_user)
    """Добавить участника в команду проекта. (Пока что возвращает заглушку)"""
    return member

@router.post("/{project_id}/curator", response_model=CuratorSchema, status_code=status.HTTP_201_CREATED)
async def add_project_curator(project_id: uuid.UUID, curator: CuratorSchema): # current_user: dict = Depends(get_current_user)
    """Назначить куратора проекта. (Пока что возвращает заглушку)"""
    return CuratorSchema(
            id=curator.id,
            firstName=curator.firstName,
            lastName=curator.lastName,
            middleName=curator.middleName
        )


#======DELETE=======#
@router.delete("/{project_id}/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_link(project_id: uuid.UUID, link_id: uuid.UUID): # current_user: dict = Depends(get_current_user)
    """Удалить ссылку на ресурс проекта. (Пока что ничего не делает)"""
    return

@router.delete("/{project_id}/team/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_member(project_id: uuid.UUID, member_id: uuid.UUID): # current_user: dict = Depends(get_current_user)
    """Удалить участника из команды проекта. (Пока что ничего не делает)"""
    return

@router.delete("/{project_id}/curator", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_curator(project_id: uuid.UUID): # current_user: dict = Depends(get_current_user)
    """Удалить куратора проекта. (Пока что ничего не делает)"""
    return

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: uuid.UUID): # current_user: dict = Depends(get_current_user)
    """Удалить проект. (Пока что ничего не делает)"""
    return

@router.delete("/{project_id}/links", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_project_links(project_id: uuid.UUID): # current_user: dict = Depends(get_current_user)
    """Удалить все ссылки на ресурсы проекта. (Пока что ничего не делает)"""
    return



#========PUT========#
@router.put("/{project_id}", response_model=ProjectFullSchemaResponse, status_code=status.HTTP_200_OK)
async def update_project(project_id: uuid.UUID, project: ProjectFullSchemaResponse): # current_user: dict = Depends(get_current_user)
    """Обновить информацию о проекте. (Пока что возвращает заглушку)"""
    return project

@router.put("/{project_id}/links/{link_id}", response_model=ProjectLink, status_code=status.HTTP_200_OK)
async def update_project_link(project_id: uuid.UUID, link_id: uuid.UUID, link: ProjectLink): # current_user: dict = Depends(get_current_user)
    """Обновить информацию о ссылке на ресурс проекта. (Пока что возвращает заглушку)"""
    return link

@router.put("/{project_id}/team/{member_id}", response_model=ProjectMemberSchema, status_code=status.HTTP_200_OK)
async def update_project_member(project_id: uuid.UUID, member_id: uuid.UUID, member: ProjectMemberSchema): # current_user: dict = Depends(get_current_user)
    """Обновить информацию об участнике команды проекта. (Пока что возвращает заглушку)"""
    return member

@router.put("/{project_id}/curator", response_model=CuratorSchema, status_code=status.HTTP_200_OK)
async def update_project_curator(project_id: uuid.UUID, curator: CuratorSchema): # current_user: dict = Depends(get_current_user)
    """Обновить информацию о кураторе проекта. (Пока что возвращает заглушку)"""
    return curator
