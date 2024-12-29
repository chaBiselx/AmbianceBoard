window.addEventListener('DOMContentLoaded', event => {

    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            offset: 74,
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

});

function modalShow(param = {
    title: "",
    body: "",
    footer: "",
    width: "m"
}) {
    const mainModal = new bootstrap.Modal(document.getElementById('mainModal'), {
        keyboard: false
    })
    document.getElementById('mainModal').classList.remove('modal-lg');
    document.getElementById('mainModal').classList.remove('modal-sm');
    document.getElementById('mainModal').classList.remove('modal-xl');
    switch (param.width) {
        case 'lg':
            width = 'modal-lg';
            break;
        case 'sm':
            width = 'modal-sm';
            break;
        case 'xl':
            width = 'modal-xl';
            break;
        default:
            width = null
            break;
    }
    console.log(width);
    console.log(document.getElementById('mainModal').classList);
    
    document.getElementById('mainModal').classList.add(width);

    
    document.getElementById("mainModalTitle").innerHTML = param.title;
    document.getElementById("mainModalBody").innerHTML = param.body;
    document.getElementById("mainModalFooter").innerHTML = param.footer;


    mainModal.show();
}

function modalHide() {
    var myModalEl = document.getElementById('mainModal');
    var modal = bootstrap.Modal.getInstance(myModalEl)
    modal.hide();

    document.getElementById("mainModalTitle").innerHTML = "";
    document.getElementById("mainModalBody").innerHTML = "";
    document.getElementById("mainModalFooter").innerHTML = "";
}
