from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.markdown as fmt
import asyncio
import sqlite3
from config import TOKEN

loop = asyncio.get_event_loop()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

connection = sqlite3.connect("C:/Users/artno/OneDrive/Рабочий стол/HSE/Bots/hse_bot")
cursor = connection.cursor()

itog_redact_CV = []
itog_delite_CV = []

keyboard_main_menu = types.InlineKeyboardMarkup()                                   #клавиатура из мейн меню (вытащим для тестов)
keyboard_main_menu.add(types.InlineKeyboardButton(text="Работа с резюме", callback_data="Работа с резюме"))
keyboard_main_menu.add(types.InlineKeyboardButton(text="Работа с проектами", callback_data="Работа с проектами"))
keyboard_main_menu.add(types.InlineKeyboardButton(text="Об авторах", callback_data="Об авторах"))

class CV_states(StatesGroup):                               #Стейты для конечных автоматов CV
    add_CV = State()
    read_CV = State()
    redact_itog_CV = State()
    update_CV = State()
    delite_CV = State()

class project_states(StatesGroup):                               #Стейты для конечных автоматов project
    add_project = State()
    read_project = State()
    redact_project = State()
    update_project = State()
    delite_project = State()

class vacancy_states(StatesGroup):                          #стейты для конечных автоматов vacancy
    add_vacancy = State()
    create_new_vacancy = State()
    delite_vacancy = State()
    delite_vacancy_itog = State()
    read_vacancy = State()
    read_vacancy_itog = State()


main_menu = ['Полетели!', 'К главному меню']                #команды для активации главного меню
about_avtors = ['Об авторах']
work_with_CV = ['Работа с резюме', 'Назад, к работе с резюме']
CV_create = ['Добавить резюме']
CV_read = ['Посмотреть свои резюме']
CV_redact = ['Редактировать резюме']
CV_delite = ['Удалить резюме']
work_with_project = ['Работа с проектами', 'Назад, к работе с проектами']
project_create = ['Добавить проекты']
project_read = ['Посмотреть проекты']
project_redact = ['Редактировать проекты']
project_delite = ['Удалить проекты']
work_with_vacancy = ['Добавить вакансии в проект', 'Назад, к работе с вакансиями']
vacancy_create = ['Добавить вакансию']
vacancy_delite = ['Удалить вакансию']
vacancy_read = ['Посмотреть вакансии']

keyboard_mistake = types.InlineKeyboardMarkup()                                           
keyboard_mistake.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))


#основные менюшки бота (не функционал)
@dp.message_handler(commands=['help'])                      #хелп для пользователя
async def send_help(message: types.Message):
    await message.answer("Привет!\nЭтот бот поможет тебе найти работника в свой проект, или работу в увлекательном проекте.\nБыстрее создавай резюме и карточку проекта!")


@dp.message_handler(commands=['start'])                     #начало работы с ботом по команде старт
async def send_welcome(message: types.Message):
    try:
        cursor.execute("SELECT count(*) FROM users WHERE tg = ?", (message.from_user.username,))
        info = cursor.fetchone()[0]
        if info == 0:
            cursor.execute('INSERT INTO users (tg, CV, project) VALUES (?, ?, ?)', (message.from_user.username, 0, 0))
            connection.commit()
        keyboard_start = types.InlineKeyboardMarkup()
        keyboard_start.add(types.InlineKeyboardButton(text="Полетели!", callback_data="Полетели!"))
        await message.answer("Привет!\nЕсли хочешь развивать свой проект, или принять участие в уже готовом проекте - этот бот для тебя!\nСкорее нажимай на кнопку 'полетели', и я тебе все расскажу", reply_markup=keyboard_start)
    except:
        await message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)

@dp.callback_query_handler(text = main_menu)                #главное меню, из которого можно попасть куда угодно
async def main_menu(callback: types.CallbackQuery):
    try:
        keyboard_main_menu = types.InlineKeyboardMarkup()
        keyboard_main_menu.add(types.InlineKeyboardButton(text="Работа с резюме", callback_data="Работа с резюме"))
        keyboard_main_menu.add(types.InlineKeyboardButton(text="Работа с проектами", callback_data="Работа с проектами"))
        vacancy_main_menu_bull = cursor.execute("SELECT * FROM project WHERE tg=?", (callback.from_user.username,))
        if vacancy_main_menu_bull.fetchone() is not None:
            keyboard_main_menu.add(types.InlineKeyboardButton(text="Добавить вакансии в проект", callback_data="Добавить вакансии в проект"))
        keyboard_main_menu.add(types.InlineKeyboardButton(text="Об авторах", callback_data="Об авторах"))
        await callback.message.answer("Приветствую тебя в главном меню!\nЗдесь ты можешь выбрать различные варианты взаимодействия с ботом", reply_markup=keyboard_main_menu)
        await callback.answer()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(text = work_with_CV)        #общий раздел работы с резюме, тут пользователь сможет посмотреть текущие резюме, добавить новые
async def work_with_CV(callback: types.CallbackQuery):
    try:
        keyboard_work_with_CV = types.InlineKeyboardMarkup()
        keyboard_work_with_CV.add(types.InlineKeyboardButton(text="Добавить резюме", callback_data="Добавить резюме"))
        keyboard_work_with_CV.add(types.InlineKeyboardButton(text="Редактировать резюме", callback_data="Редактировать резюме"))
        keyboard_work_with_CV.add(types.InlineKeyboardButton(text="Удалить резюме", callback_data="Удалить резюме"))
        keyboard_work_with_CV.add(types.InlineKeyboardButton(text="Посмотреть свои резюме", callback_data="Посмотреть свои резюме"))
        keyboard_work_with_CV.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        await callback.message.answer("В этом разделе ты можешь сделать различные вещи с твоим резюме или добавить новое", reply_markup=keyboard_work_with_CV)
        await callback.answer()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


#работа с резюме: добавление, просмотр, редактирование и удаление

@dp.callback_query_handler(text = CV_create)        #Добавить новое резюме
async def CV_create(callback: types.CallbackQuery):
    try:
        keyboard_create_CV = types.InlineKeyboardMarkup()
        keyboard_create_CV.add(types.InlineKeyboardButton(text="Назад, к работе с резюме", callback_data="Назад, к работе с резюме"))
        keyboard_create_CV.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        await callback.message.answer("Введите в ОДНОМ сообщении в первой строчке вашу профессию (не более 64 символов), а в следующей текст\nПример:\n\n\nПрограммист\nЛюблю писать ботов", reply_markup=keyboard_create_CV)
        await callback.answer()
        await CV_states.add_CV.set()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)

@dp.message_handler(state = CV_states.add_CV)       #Стейт для добавления нового резюме
async def resume(message: types.Message, state: FSMContext):
    try:
        keyboard_create_CV = types.InlineKeyboardMarkup()
        keyboard_create_CV.add(types.InlineKeyboardButton(text="Назад, к работе с резюме", callback_data="Назад, к работе с резюме"))
        keyboard_create_CV.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        await state.update_data(resume=message.text.lower())
        resume=message.text.lower()
        resume_name = resume.split("\n")[0]
        resume = resume.split('\n', 1)[1]
        cursor.execute("Update users set CV = 1 where tg = ?", (message.from_user.username,))
        cursor.execute('INSERT INTO CV (tg, name_CV, CV) VALUES (?, ?, ?)', (message.from_user.username, resume_name, resume))
        connection.commit()
        await message.answer("Ваше резюме сохранено!", reply_markup=keyboard_create_CV)
        await state.finish()
    except:
        await state.finish()
        await message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(text = CV_read)        #просмотр резюме пользователя, если они имеются
async def CV_read(callback: types.CallbackQuery):
    try:
        keyboard_CV_read = types.InlineKeyboardMarkup()
        keyboard_CV_read.add(types.InlineKeyboardButton(text="Назад, к работе с резюме", callback_data="Назад, к работе с резюме"))
        keyboard_CV_read.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        CV_bull = cursor.execute("SELECT CV FROM users WHERE tg=?", (callback.from_user.username,)).fetchone()[0]
        if CV_bull == 0:
            await callback.message.answer("У вас еще нет резюме", reply_markup=keyboard_CV_read)
            await callback.answer()
        else:
            names_CV = cursor.execute("SELECT name_CV FROM CV WHERE (tg=?)", (callback.from_user.username,)).fetchall()
            l = list(names_CV)
            itog = []
            for i in l:
                st = str(i)
                keyboard_CV_read.add(types.InlineKeyboardButton(text=st[2:-3], callback_data=st[2:-3]))
                itog.append(st[2:-3])
            await callback.message.answer("Ваши резюме:", reply_markup=keyboard_CV_read)
            await callback.answer()
            await CV_states.read_CV.set()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(state = CV_states.read_CV)       #стейт для просмотра резюме
async def print_CV(callback: types.CallbackQuery, state: FSMContext):
    try:
        keyboard_CV_read = types.InlineKeyboardMarkup()
        keyboard_CV_read.add(types.InlineKeyboardButton(text="Назад, к работе с резюме", callback_data="Назад, к работе с резюме"))
        keyboard_CV_read.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        resume_name = str(callback.data)
        resume = str(cursor.execute("SELECT CV FROM CV WHERE tg=? AND name_CV=?", (callback.from_user.username,resume_name,)).fetchone())
        resume = resume_name + '\n' + resume[2:-3]
        await callback.message.answer(resume, reply_markup=keyboard_CV_read)
        await callback.answer()
        await state.finish()
    except:
        await state.finish()
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(text = CV_redact)        #редактирование резюме
async def CV_redact(callback: types.CallbackQuery):
    try:
        keyboard_CV_redact = types.InlineKeyboardMarkup()
        keyboard_CV_redact.add(types.InlineKeyboardButton(text="Назад, к работе с резюме", callback_data="Назад, к работе с резюме"))
        keyboard_CV_redact.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        CV_bull = cursor.execute("SELECT CV FROM users WHERE tg=?", (callback.from_user.username,)).fetchone()[0]
        if CV_bull == 0:
            await callback.message.answer("У вас еще нет резюме", reply_markup=keyboard_CV_redact)
            await callback.answer()
        else:
            names_CV = cursor.execute("SELECT name_CV FROM CV WHERE (tg=?)", (callback.from_user.username,)).fetchall()
            l = list(names_CV)
            global itog_redact_CV
            itog_redact_CV = []
            for i in l:
                st = str(i)
                keyboard_CV_redact.add(types.InlineKeyboardButton(text=st[2:-3], callback_data=st[2:-3]))
                itog_redact_CV.append(st[2:-3])
            await callback.message.answer("Выберите резюме, которое хотите редактировать:", reply_markup=keyboard_CV_redact)
            await callback.answer()
            await CV_states.redact_itog_CV.set()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(state = CV_states.redact_itog_CV)                             #1 стейст состояния редактирования резюме (для вывода всех резюме)
async def CV_redact_itog(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.update_data(resume=callback.message.text.lower())
        global resume_name
        resume_name = str(callback.data)
        await callback.message.answer("Введите в ОДНОМ сообщении в первой строчке вашу профессию (не более 64 символов), а в следующей текст\nПример:\n\n\nПрограммист\nЛюблю писать ботов")
        await callback.answer()
        await CV_states.update_CV.set()
    except:
        await state.finish()
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.message_handler(state = CV_states.update_CV)                                          #2 стейт для редактирования резюме
async def CV_update(message: types.Message, state: FSMContext):
    try:
        keyboard_CV_redact = types.InlineKeyboardMarkup()
        keyboard_CV_redact.add(types.InlineKeyboardButton(text="Назад, к работе с резюме", callback_data="Назад, к работе с резюме"))
        keyboard_CV_redact.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        new_resume = str(message.text)
        new_resume_name = new_resume.split("\n")[0]
        new_resume = new_resume.split('\n', 1)[1]
        cursor.execute("Update CV set CV=? where tg=? AND name_CV=?", (new_resume, message.from_user.username, resume_name,))
        cursor.execute("Update CV set name_CV=? where tg=? AND name_CV=?", (new_resume_name, message.from_user.username, resume_name,))
        connection.commit()
        await message.answer("Ваше резюме сохранено!", reply_markup=keyboard_CV_redact)
        await state.finish()
    except:
        await state.finish()
        await message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(text = CV_delite)        #удаление резюме
async def CV_delite(callback: types.CallbackQuery):
    try:
        keyboard_CV_delite = types.InlineKeyboardMarkup()
        keyboard_CV_delite.add(types.InlineKeyboardButton(text="Назад, к работе с резюме", callback_data="Назад, к работе с резюме"))
        keyboard_CV_delite.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        CV_bull = cursor.execute("SELECT CV FROM users WHERE tg=?", (callback.from_user.username,)).fetchone()[0]
        if CV_bull == 0:
            await callback.message.answer("У вас еще нет резюме", reply_markup=keyboard_CV_delite)
            await callback.answer()
        else:
            names_CV = cursor.execute("SELECT name_CV FROM CV WHERE (tg=?)", (callback.from_user.username,)).fetchall()
            l = list(names_CV)
            global itog_delite_CV
            itog_delite_CV = []
            for i in l:
                st = str(i)
                keyboard_CV_delite.add(types.InlineKeyboardButton(text=st[2:-3], callback_data=st[2:-3]))
                itog_delite_CV.append(st[2:-3])
            await callback.message.answer("Выберите резюме, которое хотите удалить:", reply_markup=keyboard_CV_delite)
            await callback.answer()
            await CV_states.delite_CV.set()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(state = CV_states.delite_CV)         #стейт для удаления резюме
async def CV_delite_maker(callback: types.CallbackQuery, state: FSMContext):
    try:
        keyboard_just_delite = types.InlineKeyboardMarkup()
        keyboard_just_delite.add(types.InlineKeyboardButton(text="Назад, к работе с резюме", callback_data="Назад, к работе с резюме"))
        keyboard_just_delite.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        resume_name = str(callback.data)
        cursor.execute("DELETE FROM CV WHERE tg=? AND name_CV=?", (callback.from_user.username, resume_name,))
        CV_bull = cursor.execute("SELECT * FROM CV WHERE tg=?", (callback.from_user.username,))
        if CV_bull.fetchone() is None:
            cursor.execute("Update users set CV = 0 where tg = ?", (callback.from_user.username,))
        connection.commit()
        await callback.message.answer("Резюме удалено!", reply_markup=keyboard_just_delite)
        await callback.answer()
        await state.finish()
    except:
        await state.finish()
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


#работа с проектами: добавление, изменение, удаление и просмотр


@dp.callback_query_handler(text = work_with_project)            #общий раздел работы с проектами, где можно посмотреть текущие проекты, добавить новые
async def work_with_project(callback: types.CallbackQuery):
    try:
        keyboard_work_with_project = types.InlineKeyboardMarkup()
        keyboard_work_with_project.add(types.InlineKeyboardButton(text="Добавить проекты", callback_data="Добавить проекты"))
        keyboard_work_with_project.add(types.InlineKeyboardButton(text="Редактировать проекты", callback_data="Редактировать проекты"))
        keyboard_work_with_project.add(types.InlineKeyboardButton(text="Удалить проекты", callback_data="Удалить проекты"))
        keyboard_work_with_project.add(types.InlineKeyboardButton(text="Посмотреть проекты", callback_data="Посмотреть проекты"))
        keyboard_work_with_project.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        await callback.message.answer("В этом разделе ты можешь сделать различные вещи с твоим проектом или добавить новый", reply_markup=keyboard_work_with_project)
        await callback.answer()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(text = project_create)        #Добавить новый проект
async def project_create(callback: types.CallbackQuery):
    try:
        keyboard_create_project = types.InlineKeyboardMarkup()
        keyboard_create_project.add(types.InlineKeyboardButton(text="Назад, к работе с проектами", callback_data="Назад, к работе с проектами"))
        keyboard_create_project.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        await callback.message.answer("Введите в ОДНОМ сообщении в первой строчке название вашего проекта (не более 64 символов), а в следующих его описание\nПример:\n\n\nCommunityFinder\nПроект, который объединяет людей", reply_markup=keyboard_create_project)
        await callback.answer()
        await project_states.add_project.set()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.message_handler(state = project_states.add_project)       #Стейт для добавления нового проекта
async def project(message: types.Message, state: FSMContext):
    try:
        keyboard_create_project = types.InlineKeyboardMarkup()
        keyboard_create_project.add(types.InlineKeyboardButton(text="Назад, к работе с проектами", callback_data="Назад, к работе с проектами"))
        keyboard_create_project.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        await state.update_data(project=message.text.lower())
        project=message.text.lower()
        project_name = project.split("\n")[0]
        project = project.split('\n', 1)[1]
        cursor.execute("Update users set project = 1 where tg = ?", (message.from_user.username,))
        cursor.execute('INSERT INTO project (tg, name_project, project, vacancy) VALUES (?, ?, ?, 0)', (message.from_user.username, project_name, project))
        connection.commit()
        await message.answer("Ваш проект сохранен!", reply_markup=keyboard_create_project)
        await state.finish()
    except:
        await state.finish()
        await message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(text = project_read)        #просмотр проектов пользователя, если они имеются
async def project_read(callback: types.CallbackQuery):
    try:
        keyboard_project_read = types.InlineKeyboardMarkup()
        keyboard_project_read.add(types.InlineKeyboardButton(text="Назад, к работе с проектами", callback_data="Назад, к работе с проектами"))
        keyboard_project_read.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        project_bull = cursor.execute("SELECT project FROM users WHERE tg=?", (callback.from_user.username,)).fetchone()[0]
        if project_bull == 0:
            await callback.message.answer("У вас еще нет проекта", reply_markup=keyboard_project_read)
            await callback.answer()
        else:
            names_project = cursor.execute("SELECT name_project FROM project WHERE (tg=?)", (callback.from_user.username,)).fetchall()
            l = list(names_project)
            itog = []
            for i in l:
                st = str(i)
                keyboard_project_read.add(types.InlineKeyboardButton(text=st[2:-3], callback_data=st[2:-3]))
                itog.append(st[2:-3])
            await callback.message.answer("Ваши резюме:", reply_markup=keyboard_project_read)
            await callback.answer()
            await project_states.read_project.set()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(state = project_states.read_project)       #стейт для просмотра проектов
async def print_project(callback: types.CallbackQuery, state: FSMContext):
    try:
        keyboard_project_read = types.InlineKeyboardMarkup()
        keyboard_project_read.add(types.InlineKeyboardButton(text="Назад, к работе с проектами", callback_data="Назад, к работе с проектами"))
        keyboard_project_read.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        project_name = str(callback.data)
        project = str(cursor.execute("SELECT project FROM project WHERE tg=? AND name_project=?", (callback.from_user.username, project_name,)).fetchone())
        project = project_name + '\n' + project[2:-3]
        await callback.message.answer(project, reply_markup=keyboard_project_read)
        await callback.answer()
        await state.finish()
    except:
        await state.finish()
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(text = project_redact)                       #редактирование проектов
async def project_redact(callback: types.CallbackQuery):
    try:
        keyboard_project_redact = types.InlineKeyboardMarkup()
        keyboard_project_redact.add(types.InlineKeyboardButton(text="Назад, к работе с проектами", callback_data="Назад, к работе с проектами"))
        keyboard_project_redact.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        project_bull = cursor.execute("SELECT project FROM users WHERE tg=?", (callback.from_user.username,)).fetchone()[0]
        if project_bull == 0:
            await callback.message.answer("У вас еще нет проекта", reply_markup=keyboard_project_redact)
            await callback.answer()
        else:
            names_project = cursor.execute("SELECT name_project FROM project WHERE (tg=?)", (callback.from_user.username,)).fetchall()
            l = list(names_project)
            global itog_redact_project
            itog_redact_project = []
            for i in l:
                st = str(i)
                keyboard_project_redact.add(types.InlineKeyboardButton(text=st[2:-3], callback_data=st[2:-3]))
                itog_redact_project.append(st[2:-3])
            await callback.message.answer("Выберите проект, которое хотите редактировать:", reply_markup=keyboard_project_redact)
            await callback.answer()
            await project_states.redact_project.set()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(state = project_states.redact_project)                                   #1 стейст состояния редактирования проекта (для вывода всех проектов)
async def project_redact_itog(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.update_data(project=callback.message.text.lower())
        global project_name
        project_name = str(callback.data)
        await callback.message.answer("Введите в ОДНОМ сообщении в первой строчке название вашего проекта (не более 64 символов), а в следующих его описание\nПример:\n\n\nCommunityFinder\nПроект, который объединяет людей")
        await callback.answer()
        await project_states.update_project.set()
    except:
        await state.finish()
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.message_handler(state = project_states.update_project)                                          #2 стейт для редактирования проекта
async def project_update(message: types.Message, state: FSMContext):
    try:
        keyboard_project_redact = types.InlineKeyboardMarkup()
        keyboard_project_redact.add(types.InlineKeyboardButton(text="Назад, к работе с проектами", callback_data="Назад, к работе с проектами"))
        keyboard_project_redact.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        new_project = str(message.text)
        new_project_name = new_project.split("\n")[0]
        new_project = new_project.split('\n', 1)[1]
        cursor.execute("Update project set project=? where tg=? AND name_project=?", (new_project, message.from_user.username, project_name,))
        cursor.execute("Update CV set name_CV=? where tg=? AND name_CV=?", (new_project_name, message.from_user.username, project_name,))
        connection.commit()
        await message.answer("Ваше резюме сохранено!", reply_markup=keyboard_project_redact)
        await state.finish()
    except:
        await state.finish()
        await message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(text = project_delite)                                #удаление проекта
async def project_delite(callback: types.CallbackQuery):
    try:
        keyboard_project_delite = types.InlineKeyboardMarkup()
        keyboard_project_delite.add(types.InlineKeyboardButton(text="Назад, к работе с проектами", callback_data="Назад, к работе с проектами"))
        keyboard_project_delite.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        project_bull = cursor.execute("SELECT project FROM users WHERE tg=?", (callback.from_user.username,)).fetchone()[0]
        if project_bull == 0:
            await callback.message.answer("У вас еще нет проекта", reply_markup=keyboard_project_delite)
            await callback.answer()
        else:
            names_project = cursor.execute("SELECT name_project FROM project WHERE (tg=?)", (callback.from_user.username,)).fetchall()
            l = list(names_project)
            global itog_delite_project
            itog_delite_project = []
            for i in l:
                st = str(i)
                keyboard_project_delite.add(types.InlineKeyboardButton(text=st[2:-3], callback_data=st[2:-3]))
                itog_delite_project.append(st[2:-3])
            await callback.message.answer("Выберите резюме, которое хотите удалить:", reply_markup=keyboard_project_delite)
            await callback.answer()
            await project_states.delite_project.set()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(state = project_states.delite_project)         #стейт для удаления проекта
async def project_delite_maker(callback: types.CallbackQuery, state: FSMContext):
    try:
        keyboard_just_delite_project = types.InlineKeyboardMarkup()
        keyboard_just_delite_project.add(types.InlineKeyboardButton(text="Назад, к работе с проектами", callback_data="Назад, к работе с проектами"))
        keyboard_just_delite_project.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        project_name = str(callback.data)
        cursor.execute("DELETE FROM project WHERE tg=? AND name_project=?", (callback.from_user.username, project_name,))
        project_bull = cursor.execute("SELECT * FROM project WHERE tg=?", (callback.from_user.username,))
        if project_bull.fetchone() is None:
            cursor.execute("Update users set project = 0 where tg = ?", (callback.from_user.username,))
        connection.commit()
        await callback.message.answer("Проект удален!", reply_markup=keyboard_just_delite_project)
        await callback.answer()
        await state.finish()
    except:
        await state.finish()
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


#работа с вакансиями: добавление к проекту, удаление и просмотр


@dp.callback_query_handler(text = work_with_vacancy)            #общий раздел работы с вакансиями, где можно посмотреть текущие вакансии по проекту, добавить новые
async def work_with_vacancy(callback: types.CallbackQuery):
    try:
        keyboard_work_with_vacancy = types.InlineKeyboardMarkup()
        keyboard_work_with_vacancy.add(types.InlineKeyboardButton(text="Добавить вакансию", callback_data="Добавить вакансию"))
        keyboard_work_with_vacancy.add(types.InlineKeyboardButton(text="Удалить вакансию", callback_data="Удалить вакансию"))
        keyboard_work_with_vacancy.add(types.InlineKeyboardButton(text="Посмотреть вакансии", callback_data="Посмотреть вакансии"))
        keyboard_work_with_vacancy.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        await callback.message.answer("В этом разделе ты можешь сделать различные вещи с твоими вакансиями или добавить новые", reply_markup=keyboard_work_with_vacancy)
        await callback.answer()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(text = vacancy_create)                       #выбор проекта, для которого будем добавлять вакансии
async def create_new_vacancy(callback: types.CallbackQuery):
    try:
        keyboard_create_new_vacancy = types.InlineKeyboardMarkup()
        keyboard_create_new_vacancy.add(types.InlineKeyboardButton(text="Назад, к работе с вакансиями", callback_data="Назад, к работе с вакансиями"))
        keyboard_create_new_vacancy.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        project_bull = cursor.execute("SELECT project FROM users WHERE tg=?", (callback.from_user.username,)).fetchone()[0]
        if project_bull == 0:
            await callback.message.answer("У вас еще нет проекта", reply_markup=keyboard_create_new_vacancy)
            await callback.answer()
        else:
            names_project = cursor.execute("SELECT name_project FROM project WHERE (tg=?)", (callback.from_user.username,)).fetchall()
            l = list(names_project)
            for i in l:
                st = str(i)
                keyboard_create_new_vacancy.add(types.InlineKeyboardButton(text=str(st[2:-3]), callback_data=str(st[2:-3])))
            await callback.message.answer("Выберите проект, которому хотите добавить резюме:", reply_markup=keyboard_create_new_vacancy)
            await callback.answer()
            await vacancy_states.create_new_vacancy.set()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(state = vacancy_states.create_new_vacancy)                           #1 стейст состояния выбора проекта
async def add_vacancy(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.update_data(name_project=callback.data)
        await callback.message.answer("Введите в ОДНОМ сообщении в первой строчке название профессии, на которую ищете сотрудника (не более 64 символов), а в следующих описание вакансии\n\nПример:\n\n\nПрограммист\nНужен сотрудник, который умеет писать ботов")
        await callback.answer()
        await vacancy_states.add_vacancy.set()
    except:
        await state.finish()
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.message_handler(state = vacancy_states.add_vacancy)                                          #2 стейт для добавления вакансии
async def add_vacancy_itog(message: types.Message, state: FSMContext):
    try:
        name_project = await state.get_data()
        name_project = (str(name_project)[18:-2])
        keyboard_add_vacancy_itog = types.InlineKeyboardMarkup()
        keyboard_add_vacancy_itog.add(types.InlineKeyboardButton(text="Назад, к работе с вакансиями", callback_data="Назад, к работе с вакансиями"))
        keyboard_add_vacancy_itog.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        vacancy = str(message.text)
        vacancy_name = vacancy.split("\n")[0]
        vacancy = vacancy.split('\n', 1)[1]
        cursor.execute("Update project set vacancy=1 where tg=? AND name_project=?", (message.from_user.username, str(name_project),))
        cursor.execute('INSERT INTO vacancy (project_id, vacancy_name, vacancy) VALUES ((SELECT project_id FROM project WHERE tg=? AND name_project=?), ?, ?)', (message.from_user.username, name_project, vacancy_name, vacancy))
        connection.commit()
        await message.answer("Ваша вакансия сохранена!", reply_markup=keyboard_add_vacancy_itog)
        await state.finish()
    except:
        await state.finish()
        await message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(text = vacancy_delite)                       #выбор проекта, для которого будем удалять вакансии
async def delite_vacancy_project(callback: types.CallbackQuery):
    try:
        keyboard_delite_vacancy = types.InlineKeyboardMarkup()
        keyboard_delite_vacancy.add(types.InlineKeyboardButton(text="Назад, к работе с вакансиями", callback_data="Назад, к работе с вакансиями"))
        keyboard_delite_vacancy.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        project_bull = cursor.execute("SELECT project FROM users WHERE tg=?", (callback.from_user.username,)).fetchone()[0]
        if project_bull == 0:
            await callback.message.answer("У вас еще нет проекта", reply_markup=keyboard_delite_vacancy)
            await callback.answer()
        else:
            names_project = cursor.execute("SELECT name_project FROM project WHERE (tg=?)", (callback.from_user.username,)).fetchall()
            l = list(names_project)
            for i in l:
                st = str(i)
                keyboard_delite_vacancy.add(types.InlineKeyboardButton(text=str(st[2:-3]), callback_data=str(st[2:-3])))
            await callback.message.answer("Выберите проект, у которого хотите удалить вакансию:", reply_markup=keyboard_delite_vacancy)
            await callback.answer()
            await vacancy_states.delite_vacancy.set()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(state = vacancy_states.delite_vacancy)                           #1 стейст состояния выбора вакансии в проекте
async def delite_vacancy(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.update_data(name_project=callback.data)
        keyboard_delite_vacancy = types.InlineKeyboardMarkup()
        keyboard_delite_vacancy.add(types.InlineKeyboardButton(text="Назад, к работе с вакансиями", callback_data="Назад, к работе с вакансиями"))
        keyboard_delite_vacancy.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        vacancy_bull = cursor.execute("SELECT vacancy FROM project WHERE tg=? AND name_project=?", (callback.from_user.username, callback.data,)).fetchone()[0]
        if vacancy_bull == 0:
            await callback.message.answer("У вас нет вакансий в этом проекте", reply_markup=keyboard_delite_vacancy)
            await callback.answer()
            await state.finish()
        else:
            project_id = str(cursor.execute("SELECT project_id FROM project WHERE tg=? AND name_project=?", (callback.from_user.username, callback.data)).fetchall())[2:-3]
            names_vacancy = cursor.execute("SELECT vacancy_name FROM vacancy WHERE project_id=?", (project_id,)).fetchall()
            l = list(names_vacancy)
            for i in l:
                st = str(i)
                keyboard_delite_vacancy.add(types.InlineKeyboardButton(text=str(st[2:-3]), callback_data=str(st[2:-3])))
            await callback.message.answer("Выберите вакансию, которую хотите удалить:", reply_markup=keyboard_delite_vacancy)
            await callback.answer()
            await vacancy_states.delite_vacancy_itog.set()
    except:
        await state.finish()
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(state = vacancy_states.delite_vacancy_itog)                                          #2 стейт для удаления вакансии
async def delite_vacancy_itog(callback: types.CallbackQuery, state: FSMContext):
    try:
        keyboard_add_vacancy_itog = types.InlineKeyboardMarkup()
        keyboard_add_vacancy_itog.add(types.InlineKeyboardButton(text="Назад, к работе с вакансиями", callback_data="Назад, к работе с вакансиями"))
        keyboard_add_vacancy_itog.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        name_project = str(await state.get_data())[18:-2]
        vacancy_name = str(callback.data)
        project_id = str(cursor.execute("SELECT project_id FROM project WHERE tg=? AND name_project=?", (callback.from_user.username, name_project)).fetchall())[2:-3]
        cursor.execute("DELETE FROM vacancy WHERE project_id=? AND vacancy_name=?", (project_id, vacancy_name,))
        project_bull = cursor.execute("SELECT * FROM vacancy WHERE project_id=?", (project_id,))
        if project_bull.fetchone() is None:
            cursor.execute("Update project set vacancy = 0 where tg = ? AND name_project=?", (callback.from_user.username, name_project,))
        connection.commit()
        await callback.message.answer("Вакансия удалена!", reply_markup=keyboard_add_vacancy_itog)
        await callback.answer()
        await state.finish()
    except:
        await state.finish()
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(text = vacancy_read)                       #выбор проекта, для которого будем смотреть вакансии
async def read_vacancy_project(callback: types.CallbackQuery):
    try:
        keyboard_read_vacancy = types.InlineKeyboardMarkup()
        keyboard_read_vacancy.add(types.InlineKeyboardButton(text="Назад, к работе с вакансиями", callback_data="Назад, к работе с вакансиями"))
        keyboard_read_vacancy.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        project_bull = cursor.execute("SELECT project FROM users WHERE tg=?", (callback.from_user.username,)).fetchone()[0]
        if project_bull == 0:
            await callback.message.answer("У вас еще нет проекта", reply_markup=keyboard_read_vacancy)
            await callback.answer()
        else:
            names_project = cursor.execute("SELECT name_project FROM project WHERE (tg=?)", (callback.from_user.username,)).fetchall()
            l = list(names_project)
            for i in l:
                st = str(i)
                keyboard_read_vacancy.add(types.InlineKeyboardButton(text=str(st[2:-3]), callback_data=str(st[2:-3])))
            await callback.message.answer("Выберите проект, у которого хотите посмотреть вакансию:", reply_markup=keyboard_read_vacancy)
            await callback.answer()
            await vacancy_states.read_vacancy.set()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(state = vacancy_states.read_vacancy)                           #1 стейст состояния выбора вакансии в проекте
async def read_vacancy(callback: types.CallbackQuery, state: FSMContext):
    try:
        await state.update_data(name_project=callback.data)
        keyboard_read_vacancy = types.InlineKeyboardMarkup()
        keyboard_read_vacancy.add(types.InlineKeyboardButton(text="Назад, к работе с вакансиями", callback_data="Назад, к работе с вакансиями"))
        keyboard_read_vacancy.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        vacancy_bull = cursor.execute("SELECT vacancy FROM project WHERE tg=? AND name_project=?", (callback.from_user.username, callback.data,)).fetchone()[0]
        if vacancy_bull == 0:
            await callback.message.answer("У вас нет вакансий в этом проекте", reply_markup=keyboard_read_vacancy)
            await callback.answer()
            await state.finish()
        else:
            project_id = str(cursor.execute("SELECT project_id FROM project WHERE tg=? AND name_project=?", (callback.from_user.username, callback.data)).fetchall())[2:-3]
            names_vacancy = cursor.execute("SELECT vacancy_name FROM vacancy WHERE project_id=?", (project_id,)).fetchall()
            l = list(names_vacancy)
            for i in l:
                st = str(i)
                keyboard_read_vacancy.add(types.InlineKeyboardButton(text=str(st[2:-3]), callback_data=str(st[2:-3])))
            await callback.message.answer("Выберите вакансию, информацию о которой хотите увидеть:", reply_markup=keyboard_read_vacancy)
            await callback.answer()
            await vacancy_states.read_vacancy_itog.set()
    except:
        await state.finish()
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


@dp.callback_query_handler(state = vacancy_states.read_vacancy_itog)                                          #2 стейт для вывода всей инфы о вакансии
async def read_vacancy_itog(callback: types.CallbackQuery, state: FSMContext):
    try:
        keyboard_read_vacancy_itog = types.InlineKeyboardMarkup()
        keyboard_read_vacancy_itog.add(types.InlineKeyboardButton(text="Назад, к работе с вакансиями", callback_data="Назад, к работе с вакансиями"))
        keyboard_read_vacancy_itog.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        name_project = str(await state.get_data())[18:-2]
        vacancy_name = str(callback.data)
        project_id = str(cursor.execute("SELECT project_id FROM project WHERE tg=? AND name_project=?", (callback.from_user.username, name_project)).fetchall())[2:-3]
        vacancy = str(cursor.execute("SELECT vacancy FROM vacancy WHERE project_id=? AND vacancy_name=?", (project_id, vacancy_name,)).fetchone())
        vacancy = vacancy_name + "\n" + vacancy[2:-3]
        connection.commit()
        await callback.message.answer(vacancy, reply_markup=keyboard_read_vacancy_itog)
        await callback.answer()
        await state.finish()
    except:
        await state.finish()
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)



    #не на оценочку)))


@dp.callback_query_handler(text = about_avtors)             #милый раздел об авторах
async def about_avtors(callback: types.CallbackQuery):
    try:
        keyboard_about_avtors = types.InlineKeyboardMarkup()
        keyboard_about_avtors.add(types.InlineKeyboardButton(text="К главному меню", callback_data="К главному меню"))
        await callback.message.answer("Спасибо, что зашел на эту страничку.\nМеня сделал студент ВШЭ программы КНАД Новиков Артур Данилович\nОн будет очень рад, если получит за меня 10+ баллов))))", reply_markup=keyboard_about_avtors)
        await callback.answer()
    except:
        await callback.message.answer("Произошла какая-то ошибка, если вам не сложно, напишите @Thorart", reply_markup=keyboard_mistake)


#поиск новых сообщений от пользователя

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)