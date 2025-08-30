class Column {
    constructor(name, label=null, type='str', img_src=null, readonly=false) {
        this.name = name    // Название
        this.label = label  // Подпись, null - не отображать столбец
        this.type = type    // Тип: 'int', 'str', 'bool', 'img', 'tel', 'price', 'dict'
        if (img_src) {
            this.img_src = img_src // Ссылка на static c папкой img
            this.type = 'img'
        }
        this.readonly = readonly ? 'readonly' : ''
    }

    set_dict(table) {
        this.type = 'dict'
        this.dict = table.data // Для вывода в ComboBox
    }

    view_value(value) {
        if (value === null)
            return '&lt;Null&gt;'
        switch (this.type) {
            case 'bool':
                return value ? 'Да' : 'Нет'
            case 'img':
                return `<img class="cell" src=${this.img_src + value} x-on:click='imgModal.show("${this.img_src + value}")'/>` 
            case 'tel':
                return formatPhoneNumber(value)
            case 'price':
                return price_format(value)
            case 'dict':
                for (let r of this.dict) {
                    if (r.id == value)
                        return r.name
                }
                return '&lt;Unknown>&gt;'
            default:
                return value
        }
    }
}

class Table {
    constructor(resource, title, columns, commands, limit=0) {
        this.resource = resource    // Ресурс API для взаимодействия
        this.title = title          // Название таблицы
        this.columns = columns      // Перечень столбцов
        this.commands = commands    // Действия, доступные в форме
        this.data = []              // Список полученных данных
        this.rows = []              // Список для вывода в таблицу
        this.isLoad = true, // Флаг, требуется ли загружать еще данные
        this.param = {
			offset: 0,      // Текущее смещение данных
			limit: limit,   // Лимит на одну партию данных
        }
        this.total = 0      // Сколько всего данных в базе
        this.current = {}   // Для передачи в форму
        for (let col of columns)
            this.current[col.name] = null
        this.isCurrentNew = true    // Флаг, что на форме ввод новых данных
        this.lastSelectRow = null   // Для хранения объекта html
        this.error = ''             // Для хранения сообщений об ошибках
    }

    to_row(data) {
        let l = []
        for (let c of this.columns)
            if (c.label) 
                l.push(c.view_value(data[c.name]))
        return l
    }  

    get_form() {
        let form = []
        for (let c of this.columns)
            if (c.label)
                form.push(this.get_input(c))
        return form
    }

    fill_current(data) {
        for (let k in data) 
            this.current[k] = data[k]
        this.isCurrentNew = false
    }

    clear_current() {
        for (let k in this.current)
            this.current[k] = null
        this.isCurrentNew = true
    }

    setLastSelectRow(row) {
        if (this.lastSelectRow)
            this.lastSelectRow.classList.remove('selectRow')
        if (row)
            row.classList.add('selectRow')
        this.lastSelectRow = row
    }

    getFromSend() {
        let id = this.current['id'] 
        let data = {}
        for (let col of this.columns)
            if (col.name != 'id' && (this.current[col.name] || this.current[col.name] == false))
                switch (col.type) {
                    case 'int':
                    case 'price':
                        data[col.name] = Number(this.current[col.name])
                        break
                    case 'bool':
                        data[col.name] = Boolean(this.current[col.name])
                        break
                    default:
                        data[col.name] = this.current[col.name]
                }
        return [id, data]
    }

    get_input(col) {
        let attr = `id="${col.name}" name="${col.name}" ${col.readonly} x-model="activeData.current.${col.name}"`
        let label = `<label class="form-label" for="${col.name}">${col.label}</label>`
        let input = ''
        switch (col.type){
            case 'bool':
                input = `<div class="form-check"><input type="checkbox" ${attr} class="form-check-input"/>` +
                    `<label class="form-check-label " for="${col.name}">${col.label}</label></div>`
                break
            case 'dict':
                input = `<select id="${col.name}" ${attr} class="form-select">`
                input += '<option selected class="d-none" value=null>-- Не выбрано --</option>'
                for (let r of col.dict)
                    input += `<option value="${r.id}">${r.name}</option>`
                input += `</select>${label}`
                break
            case 'int':
            case 'price':
                input = `<input type="number" ${attr} min=0 class="form-control"/>${label}`
                break
            default:
                input = `<input type="text" ${attr} class="form-control"/>${label}`
        }        
        return input
    }

    load() {
        if (this.isLoad)
            getListFromAPI(this.resource, this.param, (json) => {
                if (json.data) {
                    json.data.forEach(el => {
                        this.data.push(el)
                        this.rows.push(this.to_row(el))
                    });
                    this.param.offset += this.param.limit;
                    this.total = json.total
                    if (this.data.length >= json.total)
                        this.isLoad = false
                }
            });
    }
}

class Command {
    constructor(label, action, condition='true') {
        this.label = label,
        this.action = action,
        this.condition = condition
    }
}

product_cols = [
    new Column('id', null, 'int'),
    new Column('img_path', 'Фото', 'img', '/shop/static/'),
    new Column('name', 'Название'),
    new Column('cost', 'Стоимость', 'price'),
    new Column('count', 'Количество', 'int'),
    new Column('category_id', 'Категория')
]
rproduct_cols = [
    new Column('order_id', 'Заказ'),
    new Column('date_return', 'Дата возрата'),
    new Column('reason', 'Причина'),
    new Column('name', 'Название'),
    new Column('cost', 'Стоимость', 'price'),
    new Column('count', 'Количество', 'int'),
    new Column('category_id', 'Категория')
]
address_cols = [
    new Column('id', null, 'int'),
    new Column('img_path', 'Карта', 'img', '/general/static/'),
    new Column('address', 'Город'),
    new Column('city', 'Адрес')
]
category_cols = [
    new Column('id', null, 'int'),
    new Column('name', 'Категория')
]
user_cols = [
    new Column('id', null, 'int'),
    new Column('login', 'Логин', 'str', null, true),
    new Column('password'),
    new Column('telephone', 'Телефон', 'tel', null, true),
    new Column('email', 'Почта', 'str', null, true),
    new Column('is_admin', 'Права администратора', 'bool'),
]

clear = new Command('Новый', (table) => {
    table.clear_current()
    table.setLastSelectRow(null)
}, false)
insert = new Command('Добавить', (table) => {
    let [_, data] = table.getFromSend()
    sendToAPI(table.resource, data, 'POST', (status, json) => {
        if (status == 201) {
            table.data.push(json.data)
            table.rows.push(table.to_row(json.data))
            table.total = json.total
            setTimeout(() => {
                let doc = document.getElementById('v-pills-site')
                let rows = doc.getElementsByTagName('tr')
                table.setLastSelectRow(rows[rows.length - 1])
            }, 10);
            table.error = ''
        }
        else
            table.error = json.message
    })
}, true)
update = new Command('Обновить', (table) => {
    let [id, data] = table.getFromSend()
    sendToAPI(`${table.resource}${id}`, data, 'PATCH', (status, json) => {
        if (status == 200) {
            for (let i = 0; i < table.data.length; i++) {
                if (table.data[i].id == json.data.id) {
                    table.data[i] = json.data
                    table.rows[i] = table.to_row(json.data)
                    break
                }
            }
            table.total = json.total
            table.error = ''
        }
        else
            table.error = json.message
    })
}, false)
remove = new Command('Удалить', (table) => {
    id = table.current.id
    sendToAPI(`${table.resource}${id}`, null, 'DELETE', (status, json) => {
        if (status == 200) {
            for (let i = 0; i < table.data.length; i++) {
                if (table.data[i].id == id) {
                    table.data.splice(i, 1)
                    table.rows.splice(i, 1)
                    break
                }
            }
            table.total = json.total
            table.clear_current()
            table.setLastSelectRow(null)
            table.error = ''
        }
        else if (status == 500)
            table.error = 'Не удалось удалить данные'
        else
            table.error = json.message
    })
}, false)
commands = [clear, insert, update, remove]

categories = new Table('categories/', 'Категории', category_cols, commands)
products = new Table('products/', 'Товары', product_cols, commands, 10)
addresses = new Table('addresses/', 'Адреса', address_cols, commands, 30)
users = new Table('users/', 'Пользователи', user_cols, [update, remove], 10)
product_cols[5].set_dict(categories)
rproduct_cols[6].set_dict(categories)

function getAccountData() {
    return {
        activeData: null,
        tables: [
            products,
            addresses,
            categories,
            users
        ],
        isPosLoad: true,
        initData: function() {
            categories.load()
            addresses.load()
            users.load()
            setTimeout(() => { products.load() }, 250);
            setTimeout(() => { this.activeData = products }, 750);
        },
        changeActiveData: function(data) {
            this.activeData = data
            this.activeData.setLastSelectRow(null)            
        },
        selectRow: function(data, row) {
            this.activeData.setLastSelectRow(row) 
            this.activeData.fill_current(data)
        },
		checkPosition: function() {
            if (this.activeData instanceof Table)  {
                const height = document.body.offsetHeight
                const screenHeight = window.innerHeight
                const scrolled = window.scrollY
                const threshold = height - screenHeight / 4
                const position = scrolled + screenHeight
                if (position >= threshold && this.isPosLoad) {
                    this.activeData.load()
                    this.isPosLoad = false
                    setTimeout(() => { this.isPosLoad = true }, 100)
                }
            }			
		}
    }
}

reset = new Command('Сбросить', (setError, profile) => {
    let doc = document.getElementById('v-pills-profile')
    let inputs = doc.getElementsByTagName('input')
    for (let i of inputs)
        switch (i.id) {
            case 'rlogin':
                i.value = profile.login
                break
            case 'telephone':
                i.value = profile.telephone
                break
            case 'email':
                i.value = profile.email
                break
            default:
                i.value = ''
        }
})
updateU = new Command('Изменить', (setError, profile) => {
    let formError = '';
    form = getFormData('profileForm');
    // Проверка наличия данных в полях
    not_empty = new Map([
        ['login', 'логина'], ['telephone', 'телефона']
    ])
    formError = getMsgEmptyFields(form, not_empty)
    // Проверка корректности данных
    if (form.telephone && !/^\d{10}$/.test(form.telephone))
        formError += 'Номер телефона имеет неверный формат. ';
    if (form.email && !/^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$/.test(form.email))
        formError += 'Электронная почта имеет неверный формат. ';
    if (form.pass && forge_sha256(form.pass) != profile.password)
        formError += 'Старый пароль не верный. ';
    if ((form.pass1 || form.pass2) && form.pass1 != form.pass2)
        formError += 'Новые пароли не совпадают. ';
    if (!form.pass && form.pass1)
        formError += 'Не указан старый пароль. ';
    if (formError) {
        setError(formError)
        return
    }
    data = {
        login: form.login,
        telephone: form.telephone
    };
    if (form.pass1)
        data['password'] = forge_sha256(form.pass1)
    if (form.email)
        data['email'] = form.email
    sendToAPI(`users/${profile.id}`, data, 'PATCH', (status, json) => {
        if (status == 200) {
            for (k in json.data)
                profile[k] = json.data[k]
            setError('')
        }
        else if (status == 304) {
            setError('Не было зафиксировано изменений в данных')	
        }
        else if (json.message.indexOf('already exists') > 0)							
            setError(json.message.replace(/^.*\(([\w]+)\)=\(([\w]+)\).*$/, '$1 $2 уже имеется в базе.').
                replace('login', 'Логин').replace('telephone', 'Номер телефона'))
        else
            setError(`Ошибка на сервере: ${json.message}.`)		
    })
})

function getProfile() {
    return {
        formError: '',
        commands: [reset, updateU],
        profile: null,
        initProfile: function(id) {
            let url = `http://127.0.0.1:5000/api/v1/users/${id}`
            fetch(url)
            .then((response) => response.json())
            .then((json) => {
                this.profile = json.data
                reset.action((e) => { this.formError = e }, this.profile)
            })
            .catch((e) => { this.formError = e })
        }
    }
}