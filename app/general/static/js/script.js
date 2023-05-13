
function getListFromAPI(resource, data, func) {
	url = `http://127.0.0.1:5000/api/v1/${resource}/?` +
		new URLSearchParams(data)
	fetch(url)
		.then((response) => response.json())
		.then(func)
		.catch(console.error);
}

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
							console.log(tc.length)
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
	