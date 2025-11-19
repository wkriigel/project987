function validateVIN() {
  var vin = document.forms["search"]["vin"].value;

  if (vin == "") {
    swal("Empty?", "Please enter a valid 17-character VIN or 5-digit Porsche serial number.", "info");
    return false;
  }

  if ( vin.length == 17 ) {
    return true;
  } else if (vin.length == 5) {
    return true;
  } else {
    Swal.fire({
      icon: 'error',
      title: 'Invalid VIN',
      text: "Please enter a valid 17-character VIN or 5-digit Porsche serial number.",
      confirmButtonColor: '#f15a29'
    });
    return false;
  }
}

function upperCaseF(e) {
  var ss = e.target.selectionStart;
  var se = e.target.selectionEnd;
  // Removes whitespace and replaces the letter 'O' with Zero and the letter 'I' with 1.
  // Does not subsitute the letter 'Q' with the number 9 due to potential confusion.
  e.target.value = e.target.value.toUpperCase().replace(/\s+/g, '').replace(/O/g,'0').replace(/I/g,'1');
  e.target.selectionStart = ss;
  e.target.selectionEnd = se;
}