document.addEventListener('DOMContentLoaded', function() {
    const spendSourceSelect = document.querySelector('#spend_source');
    const creditCardSection = document.querySelector('#credit-card-section');
    const fundsSection = document.querySelector('#funds-section');

    function updateSections() {
        const spendSource = spendSourceSelect.value;
        creditCardSection.style.display = spendSource === 'credit card' ? 'block' : 'none';
        fundsSection.style.display = spendSource === 'funds' ? 'block' : 'none';
    }

    spendSourceSelect.addEventListener('change', updateSections);
    updateSections(); // Initial call to set visibility based on default value
});
