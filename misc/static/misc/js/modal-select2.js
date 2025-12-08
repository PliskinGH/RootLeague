document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.crispyFormsetModal !== "undefined") {
        window.crispyFormsetModal.onFormAdded = function (event) {
            $('.django-select2').djangoSelect2()
        };
        window.crispyFormsetModal.onModalFormOpened = function (modalForm) {
            $('.django-select2').djangoSelect2()
        };
    };

    // select all bootstrap modals
    const elements = document.querySelectorAll('.modal');

    // attach select2 to modal parent
    elements.forEach(element => {
        element.addEventListener('show.bs.modal', function(e) {
            const elementSelect2 = element.querySelector('.django-select2');
            $('.django-select2').djangoSelect2({
                dropdownParent: elementSelect2.parentElement
            });
        });
    });
});