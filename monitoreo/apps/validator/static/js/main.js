function loadingButton(button) {
    button.form.submit();
    button.disabled = true;
    button.classList.add('state-loading');
}