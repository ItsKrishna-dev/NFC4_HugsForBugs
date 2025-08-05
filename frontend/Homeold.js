let next = document.querySelector('.next')
let prev = document.querySelector('.prev')

next.addEventListener('click', ()=>{
    let items = document.querySelectorAll('.item')
    document.querySelector('.slide').appendChild(items[0])
})

prev.addEventListener('click',()=>{
    let items = document.querySelectorAll('.item')
    document.querySelector('.slide').prepend(items[items.length - 1]) // here the length of items = 6
})

// Get modal and button elements
var modal = document.getElementById('profileModal');
var btn = document.getElementById('profileButton');
var closeBtn = document.getElementsByClassName('close')[0];

// Show modal when clicking the profile button
btn.onclick = function() {
  modal.style.display = 'block';
}

// Close modal when clicking the close button
closeBtn.onclick = function() {
  modal.style.display = 'none';
}

// Close modal when clicking outside of the modal content
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = 'none';
  }
}


function toggleInput(inputId) {
  var inputSection = document.getElementById(inputId);
  if (inputSection.style.display === "none") {
    inputSection.style.display = "flex";
  } else {
    inputSection.style.display = "none";
  }
}

function saveInput(fieldId) {
  var fieldElement = document.getElementById(fieldId);
  var fieldValue = fieldElement.value;

  if (fieldValue) {
        alert("Saved: " + fieldValue);
        fieldElement.value = '';
    // You can add functionality to actually save this data
  } else {
    alert("Please fill in the field");
  }
}

// DOM references
const profileToggleBtn = document.getElementById('profileToggleBtn');
const profilePanel = document.getElementById('profilePanel');
const profileCloseBtn = document.getElementById('profileCloseBtn');
const profileForm = document.getElementById('profileForm');

if (profileToggleBtn && profilePanel && profileCloseBtn && profileForm) {
  
  // Open profile panel on toggle button click
  profileToggleBtn.addEventListener('click', () => {
    profilePanel.classList.add('open');
    profilePanel.setAttribute('aria-hidden', 'false');
  });

  // Close profile panel on close button click
  profileCloseBtn.addEventListener('click', () => {
    profilePanel.classList.remove('open');
    profilePanel.setAttribute('aria-hidden', 'true');
  });

  // Close profile panel if user clicks outside content area
  profilePanel.addEventListener('click', (e) => {
    if (e.target === profilePanel) {
      profilePanel.classList.remove('open');
      profilePanel.setAttribute('aria-hidden', 'true');
    }
  });

  // Handle form submit
  profileForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const mobile = document.getElementById('mobileInput').value.trim();
    const city = document.getElementById('cityInput').value.trim();

    // TODO: Add validation or backend saving logic here

    alert(`Saved!\nMobile: ${mobile}\nCity: ${city}`);
    profilePanel.classList.remove('open');
    profilePanel.setAttribute('aria-hidden', 'true');
  });
}


