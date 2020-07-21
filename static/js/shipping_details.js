var radioBtns = document.getElementsByName("gridRadios")
var btnProceed = document.getElementById("proceed-btn")
var checkoutbtn = document.getElementById("checkoutbtn")
btnProceed.addEventListener('click', function(){
    var action = this.dataset.action;
    var addressId = getAddressID();
    console.log('addressId=', addressId, 'action=', action )
    if(user == 'AnonymousUser'){
        console.log('User is Not Authenticated');
    }
    else{
        console.log('User is Authenticated');
        linkAddress(addressId,action);
    }
    this.style.display = "none"
    checkoutbtn.style.display = "block";
})
function getAddressID(){
    console.log("into the func")
    for(var i=0; i < radioBtns.length; i++){
        console.log("inside for loop")
        if (radioBtns[i].checked == true){
                var addressId = radioBtns[i].dataset.addressid
                console.log('inner_addressId=', addressId)
                return addressId
            }
    }
}

function linkAddress(addressId,action){
    url = "/books/link_address/";
    fetch(url, {
            method:'POST',
            headers:{
                'Content-Type':'application/json',
                'X-CSRFToken': csrftoken,
            },
            body:JSON.stringify({
                'shippingId':addressId,
                'action':action,
            })
        })
    .then((response) =>{
        return response.json()
    })
    .then((data) =>{
        console.log(data)
    })
}
