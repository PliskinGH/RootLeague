document.addEventListener('DOMContentLoaded', function() {
    // select all bootstrap modals
    const elements = document.querySelectorAll('.modal');

    // attach select2 to modal parent
    elements.forEach(element => {
        element.addEventListener('show.bs.modal', function(e) {
            $('.django-select2').djangoSelect2({
                dropdownParent: this
            })
        });
    });
});