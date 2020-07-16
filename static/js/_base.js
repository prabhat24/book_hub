var update_btns = document.getElementsByClassName("update-cart")

for(var i=0; i < update_btns.length; i++){
    update_btns[i].addEventListener('click', function(){
        var book_id = this.dataset.book
        var action = this.dataset.action
        console.log('book_id=', book_id, 'action=', action )
        if(user == 'AnonymousUser'){
            console.log('User is Not Authenticated')
        }
        else{
            console.log('User is Authenticated')
            updateUserOrder(book_id,action)
        }
    })
}

function updateUserOrder(productId, action){
    url = "/books/update_cart/";
    fetch(url, {
            method:'POST',
            headers:{
                'Content-Type':'application/json',
                'X-CSRFToken': csrftoken,
            },
            body:JSON.stringify({
                'productId':productId,
                'action':action,
            })
        })
    .then((response) =>{
        return response.json()
    })
    .then((data) =>{
        console.log(data)
        location.reload()
    })
}