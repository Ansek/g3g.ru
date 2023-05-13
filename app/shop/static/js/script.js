function dataProducts(c_id, limit) {
	return {
		products: [],
		data: {
			category: c_id,
			offset: 0,
			limit: limit
		}, 
		isLoad: true,
		cost_to: '',
		cost_from: '',
		loadProducts: function() {
			if (this.isLoad)
				getListFromAPI('products', this.data, (json) => {
					if (json.data) {
						tp = this.products
						console.log(json.data)
						json.data.forEach(el => tp.push(el));
						this.data.offset += this.data.limit;
						if (this.products.length == json.total)
							this.isLoad = false
					}
				});
		},
		findProducts: function() {
			if (this.cost_from == '')
				delete this.data.geCost
			else
				this.data.geCost = this.cost_from
			if (this.cost_to == '')
				delete this.data.leCost
			else
				this.data.leCost = this.cost_to
			this.isLoad = true;
			this.products = []
			this.data.offset = 0
			this.loadProducts()
		},
		checkPosition: function() {
			const height = document.body.offsetHeight
			const screenHeight = window.innerHeight
			const scrolled = window.scrollY
			const threshold = height - screenHeight / 4
			const position = scrolled + screenHeight
			if (position >= threshold) {
				this.loadProducts()
			}			
		},
	};
}
	