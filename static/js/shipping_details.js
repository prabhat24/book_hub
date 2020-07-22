var radioBtns = document.getElementsByName("gridRadios")
var btnProceed = document.getElementById("proceed-btn")
var checkoutbtn = document.getElementById("checkoutbtn")
btnProceed.addEventListener('click', function(){
    var action = this.dataset.action;
    var addressId = getAddressID();
    console.log('addressId=', addressId, 'action=', action )
    if(user != 'AnonymousUser'){
        console.log('User is Authenticated');
        if(radioBtns.length == 0){
            alert("please Add the address before proceeding!");
            return;
        }
        if(!isOneChecked(radioBtns)){
            console.log("hey here!!")
            alert("please select address!");
            return;
        }
        linkAddress(addressId,action);
    }
    this.style.display = "none"
    checkoutbtn.style.display = "block";
})

function isOneChecked(randioBtns) {
  for (var i=0; i<randioBtns.length; i++) {
    if (radioBtns[i].checked) {
      return true;
    }
  }
  // End of the loop, return false
  return false;
}

function getAddressID(){
    for(var i=0; i < radioBtns.length; i++){
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
