(function () {
  'use strict';

  const search = document.querySelector('[data-admin-shortcuts-search]');
  const shortcuts = document.querySelector('[data-admin-shortcuts]');
  const emptyState = document.querySelector('[data-admin-shortcuts-empty]');

  if (!search || !shortcuts) return;

  const links = Array.from(shortcuts.querySelectorAll('a'));

  function filterShortcuts() {
    const query = search.value.trim().toLocaleLowerCase();
    let visibleCount = 0;

    links.forEach(function (link) {
      const matches = link.textContent.toLocaleLowerCase().includes(query);
      link.hidden = !matches;
      if (matches) visibleCount += 1;
    });

    if (emptyState) emptyState.hidden = visibleCount !== 0;
  }

  search.addEventListener('input', filterShortcuts);
  document.addEventListener('keydown', function (event) {
    if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey) {
      const target = event.target;
      const isTyping = target && (target.isContentEditable || /INPUT|TEXTAREA|SELECT/.test(target.tagName));
      if (!isTyping) {
        event.preventDefault();
        search.focus();
      }
    }
    if (event.key === 'Escape' && document.activeElement === search) {
      search.value = '';
      filterShortcuts();
      search.blur();
    }
  });
})();
