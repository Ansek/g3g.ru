function getListFromAPI(resource, data, func) {
	let url = `http://127.0.0.1:5000/api/v1/${resource}/?` +
		new URLSearchParams(data)
	fetch(url)
		.then((response) => response.json())
		.then(func)
		.catch(console.error);
}

async function sendToAPI(resource, data, method, func) {
	let url = `http://127.0.0.1:5000/api/v1/${resource}/`
	try {
		const response = await fetch(url, {
			method: method,
			body: JSON.stringify(data),
			headers: {
				'Content-Type': 'application/json',
			}
		});
		json = ''
		if (response.status != 204)
			json = await response.json();
		if (!response.ok)
			console.log(json)
		func(response.status, json)
	} catch (err) {
		console.log(err)
	}
}

// Получение полей из формы
function getFormData(formId) {
	let form = document.getElementById(formId);
	let fd = new FormData(form);
	let data = Object.fromEntries(fd.entries());
	return data
}

// Формирование сообщения о пустых полях
function getMsgEmptyFields(form, dict) {
	let res = ''
	let msg = new Array()
	let count = 0
	for (var [k, v] of dict)
	{
		if (!form[k]) {
			msg.push(v)
			count++;
		}
	}
	if (count == 1)
		res = `Требуется заполнить поле ${msg[0]}. `
	else if (count > 1) {
		res = `Требуется заполнить поля ${msg.join(", ")}. `
		i = res.lastIndexOf(',')
		res = res.slice(0, i) + ' и' + res.slice(i+1)
	}
	return res
}

// Получение списка категорий
function dataCategories() {
	return {
		categories: null, 
		loadCategories: function() {
			getListFromAPI('categories', {limit: 10}, (json) => {
				this.categories = json.data;
			});
		}
	}
}

// Для загрузки на главной странице 
function dataIndexProducts(cn, pn) {
	return {
		categories: [], 
		loadProducts: function() {
			// Загрузка списка категорий
			getListFromAPI('categories', {}, (json) => {
				let tc = this.categories
				for (i = 0; i < cn; i++) {
					let c = json.data[i]
					// Загрузка первых двух связанных продуктов
					getListFromAPI('products', {category: c.id}, (json) => {
						if (json.total > pn) {
							tc.push({
								id: c.id,
								name: c.name, 
								products: json.data.slice(0, pn)
							})			
						}
					});
				};
			});
		}
	};
}

// Для работы с текущим пользователем
function dataUser() {
	return {
		formError: '',
		loginUser: function() {
			this.formError = '';
			form = getFormData('loginForm');
			// Проверка наличия данных в полях
			not_empty = new Map([
				['login', 'логина'], ['pass', 'пароля']
			])
			this.formError = getMsgEmptyFields(form, not_empty)
			if (this.formError)
				return;
			data = {
				login: form.login,
				password: forge_sha256(form.pass),
				remember: document.getElementById('remember').checked
			};
			sendToAPI('session/login', data, 'POST', (status, json) => {
				if (status == 204)
					location.reload()
				else if (status == 401)
					this.formError = 'Неверный пароль или логин.'
				else
					this.formError = `Ошибка на сервере: ${json.message}.`
			})
		},
		registerUser: function() {
			this.formError = '';
			form = getFormData('registrationForm');
			// Проверка наличия данных в полях
			not_empty = new Map([
				['login', 'логина'], ['pass1', 'пароля'], 
				['pass2', 'повтора пароля'], ['telephone', 'телефона']
			])
			this.formError = getMsgEmptyFields(form, not_empty)
			// Проверка корректности данных
			if (form.pass1 != form.pass2)
				this.formError += 'Пароли не совпадают. ';
			if (form.telephone && !/^\d{10}$/.test(form.telephone))
				this.formError += 'Номер телефона имеет неверный формат. ';
			if (form.email && !/^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$/.test(form.email))
				this.formError += 'Электронная почта имеет неверный формат. ';
			if (this.formError)
				return;
			data = {
				login: form.login,
				password: forge_sha256(form.pass1),
				telephone: form.telephone
			};
			if (form.email)
				data['email'] = form.email
			sendToAPI('users', data, 'POST', (status, json) => {
				if (status == 201) {
					data2 = {
						login: json.data.login,
						password: json.data.password
					};
					sendToAPI('session/login', data2, 'POST', (status, json) => {
						if (status == 204)
							location.reload()
						else 
							this.formError = `Ошибка на сервере: ${json.message}.`
					})
				}
				else if (json.message.indexOf('already exists') > 0)							
					this.formError = json.message.replace(/^.*\(([\w]+)\)=\(([\w]+)\).*$/, '$1 $2 уже имеется в базе.').
						replace('login', 'Логин').replace('telephone', 'Номер телефона')
				else
					this.formError = `Ошибка на сервере: ${json.message}.`		
			})
		} 
	}
}

function logoutUser() {
	sendToAPI('session/logout', null, 'POST', (status, json) => {
		if (status == 204)
			location.reload()
		else
			alert(`Ошибка на сервере: ${json.message}.`)
	})
}