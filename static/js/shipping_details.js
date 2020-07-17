var radioBtns = document.getElementsByName("gridRadios")
var btnProceed = document.getElementById("proceed-btn")
btnProceed.addEventListener('click', function(){
    var action = this.dataset.action
    var addressId
    for(var i; i < radioBtns.length; i++){
        if (radioBtns[i].checked == true){
            addressId = radioBtns[i].dataset.addressid
        }
    }
    console.log('addressId=', addressId, 'action=', action )
    if(user == 'AnonymousUser'){
        console.log('User is Not Authenticated')
    }
    else{
        console.log('User is Authenticated')
        linkAddress(addressId,action)
    }
})
function linkAddress(addressId,action){
    url = "/books/link_address/";
    fetch(url, {
            method:'POST',
            headers:{
                'Content-Type':'application/json',
                'X-CSRFToken': csrftoken,
            },
            body:JSON.stringify({
                'action':action,
                'shipping_id': addressId
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