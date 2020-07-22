shippingBtn=document.getElementById('add-shipping-details-btn');
shippingBtn.addEventListener('click', function(){
        items=this.dataset.items;
        if (items==0){
            alert("No items added to cart")
        }
        else{
            window.location.href = '/books/ship/';
        }
    }
)