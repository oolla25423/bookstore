const API_BASE = "http://localhost:8000/api";
let currentUser = null;
let token = localStorage.getItem("token");
let cart = JSON.parse(localStorage.getItem("cart")) || [];
let currentBook = null;
let currentPage = 1;
let currentFilters = {};

document.addEventListener("DOMContentLoaded", () => {
  initializeApp();
});

async function initializeApp() {
  if (token) {
    try {
      await loadUserData();
    } catch (error) {
      console.error("Ошибка загрузки данных пользователя:", error);
      logout();
    }
  }

  updateCartCount();

  showPage("books");
}

async function loadUserData() {
  const response = await fetchAPI("/users/", "GET", null, true);
  if (response.ok) {
    const data = await response.json();
    if (data.results && data.results.length > 0) {
      currentUser = data.results[0];
      updateUIForLoggedInUser();
    }
  } else {
    throw new Error("Не удалось загрузить данные пользователя");
  }
}

function updateUIForLoggedInUser() {
  document.getElementById("login-btn").style.display = "none";
  document.getElementById("register-btn").style.display = "none";
  document.getElementById("user-menu").style.display = "flex";
  document.getElementById("user-name").textContent = currentUser.username;
  document.getElementById("orders-nav").style.display = "block";
  document.getElementById("orders-mobile-nav").style.display = "block";
}

function updateUIForGuest() {
  document.getElementById("login-btn").style.display = "inline-flex";
  document.getElementById("register-btn").style.display = "inline-flex";
  document.getElementById("user-menu").style.display = "none";
  document.getElementById("orders-nav").style.display = "none";
  document.getElementById("orders-mobile-nav").style.display = "none";
}

async function handleLogin(event) {
  event.preventDefault();
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;

  try {
    const response = await fetchAPI("/login/", "POST", { username, password });
    if (response.ok) {
      const data = await response.json();
      token = data.access;
      localStorage.setItem("token", token);
      currentUser = data.user;

      closeModal("login-modal");
      updateUIForLoggedInUser();
      showToast("Вход выполнен успешно!", "success");
      showPage("books");
    } else {
      const error = await response.json();
      showToast(
        "Ошибка входа: " + (error.detail || "Неверные данные"),
        "error",
      );
    }
  } catch (error) {
    showToast("Ошибка соединения с сервером", "error");
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const username = document.getElementById("register-username").value;
  const email = document.getElementById("register-email").value;
  const first_name = document.getElementById("register-firstname").value;
  const last_name = document.getElementById("register-lastname").value;
  const password = document.getElementById("register-password").value;
  const password_confirm = document.getElementById("register-confirm").value;

  if (password !== password_confirm) {
    showToast("Пароли не совпадают!", "error");
    return;
  }

  try {
    const response = await fetchAPI("/register/", "POST", {
      username,
      email,
      first_name,
      last_name,
      password,
      password_confirm,
    });

    if (response.ok) {
      const data = await response.json();
      token = data.access;
      localStorage.setItem("token", token);
      currentUser = data.user;

      closeModal("register-modal");
      updateUIForLoggedInUser();
      showToast("Регистрация успешна!", "success");
      showPage("books");
    } else {
      const error = await response.json();
      const errorMsg = Object.values(error).flat().join(", ");
      showToast("Ошибка регистрации: " + errorMsg, "error");
    }
  } catch (error) {
    showToast("Ошибка соединения с сервером", "error");
  }
}

function logout() {
  token = null;
  currentUser = null;
  localStorage.removeItem("token");
  updateUIForGuest();
  showToast("Вы вышли из системы", "info");
  showPage("books");
}

async function fetchAPI(
  endpoint,
  method = "GET",
  data = null,
  requireAuth = false,
) {
  const headers = {
    "Content-Type": "application/json",
  };

  if (requireAuth && token) {
    headers["Authorization"] = `Bearer ${token}`;
  } else if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const config = {
    method,
    headers,
  };

  if (data && (method === "POST" || method === "PUT" || method === "PATCH")) {
    config.body = JSON.stringify(data);
  }

  return await fetch(API_BASE + endpoint, config);
}

function showPage(pageName) {
  document.querySelectorAll(".page").forEach((page) => {
    page.classList.remove("active");
  });

  const page = document.getElementById(pageName + "-page");
  if (page) {
    page.classList.add("active");
  }

  switch (pageName) {
    case "books":
      loadBooks();
      loadAuthorsFilter();
      break;
    case "authors":
      loadAuthors();
      break;
    case "orders":
      if (!token) {
        showToast("Необходимо войти в систему", "warning");
        showLoginModal();
        return;
      }
      loadOrders();
      break;
  }
}

function toggleMobileMenu() {
  const menu = document.getElementById("mobile-menu");
  menu.classList.toggle("active");
}

function showLoginModal() {
  document.getElementById("login-modal").classList.add("active");
}

function showRegisterModal() {
  document.getElementById("register-modal").classList.add("active");
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.remove("active");
}

window.addEventListener("click", (event) => {
  if (event.target.classList.contains("modal")) {
    event.target.classList.remove("active");
  }
});

async function loadBooks() {
  const booksListDiv = document.getElementById("books-list");
  booksListDiv.innerHTML =
    '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Загрузка...</div>';

  let url = `/books/?page_size=100`;

  if (currentFilters.search) {
    url += `&search=${encodeURIComponent(currentFilters.search)}`;
  }
  if (currentFilters.author) {
    url += `&author=${currentFilters.author}`;
  }
  if (currentFilters.ordering) {
    url += `&ordering=${currentFilters.ordering}`;
  }

  try {
    const response = await fetchAPI(url);
    if (response.ok) {
      const data = await response.json();
      displayBooks(data.results);
    } else {
      booksListDiv.innerHTML =
        '<p class="text-center text-muted">Ошибка загрузки книг</p>';
    }
  } catch (error) {
    booksListDiv.innerHTML =
      '<p class="text-center text-muted">Ошибка соединения</p>';
  }
}

function displayBooks(books) {
  const booksListDiv = document.getElementById("books-list");

  if (books.length === 0) {
    booksListDiv.innerHTML =
      '<p class="text-center text-muted">Книги не найдены</p>';
    return;
  }

  booksListDiv.innerHTML = "";
  books.forEach((book) => {
    const bookCard = createBookCard(book);
    booksListDiv.appendChild(bookCard);
  });
}

function createBookCard(book) {
  const card = document.createElement("div");
  card.className = "book-card";
  card.onclick = () => showBookDetail(book.id);

  const stockStatus =
    book.stock > 0
      ? `<span class="book-stock">В наличии: ${book.stock} шт.</span>`
      : '<span class="book-stock out-of-stock">Нет в наличии</span>';

  const bookImageHtml = book.cover_image
    ? `<img src="${escapeHtml(book.cover_image)}" alt="${escapeHtml(book.title)}" style="width: 100%; height: 100%; object-fit: cover;">`
    : `<i class="fas fa-book"></i>`;

  card.innerHTML = `
        <div class="book-image">
            ${bookImageHtml}
        </div>
        <div class="book-content">
            <h3 class="book-title">${escapeHtml(book.title)}</h3>
            <p class="book-author">
                <i class="fas fa-user-pen"></i> ${escapeHtml(book.author.name)}
            </p>
            <p class="book-description">${escapeHtml(book.description || "Нет описания")}</p>
            <div class="book-footer">
                <span class="book-price">${book.price} ₽</span>
                ${stockStatus}
            </div>
        </div>
    `;

  return card;
}

async function showBookDetail(bookId) {
  const contentDiv = document.getElementById("book-detail-content");
  contentDiv.innerHTML =
    '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Загрузка...</div>';

  showPage("book-detail");

  try {
    const response = await fetchAPI(`/books/${bookId}/`);
    if (response.ok) {
      const book = await response.json();
      currentBook = book;
      displayBookDetail(book);
      loadReviews(bookId);
    } else {
      contentDiv.innerHTML =
        '<p class="text-center text-muted">Ошибка загрузки книги</p>';
    }
  } catch (error) {
    contentDiv.innerHTML =
      '<p class="text-center text-muted">Ошибка соединения</p>';
  }
}

function displayBookDetail(book) {
  const contentDiv = document.getElementById("book-detail-content");

  const addToCartBtn =
    book.stock > 0
      ? `<button class="btn btn-primary" onclick="addToCart(${book.id})">
                <i class="fas fa-cart-plus"></i> Добавить в корзину
            </button>`
      : `<button class="btn btn-danger" disabled>
                <i class="fas fa-times"></i> Нет в наличии
            </button>`;

  const detailImageHtml = book.cover_image
    ? `<img src="${escapeHtml(book.cover_image)}" alt="${escapeHtml(book.title)}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px;">`
    : `<i class="fas fa-book"></i>`;

  contentDiv.innerHTML = `
        <div class="book-detail">
            <div class="book-detail-header">
                <div class="book-detail-image">
                    ${detailImageHtml}
                </div>
                <div class="book-detail-info">
                    <h2>${escapeHtml(book.title)}</h2>
                    <div class="book-detail-meta">
                        <div class="meta-item">
                            <i class="fas fa-user-pen"></i>
                            <span>Автор: <strong>${escapeHtml(book.author.name)}</strong></span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-ruble-sign"></i>
                            <span>Цена: <strong>${book.price} ₽</strong></span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-boxes-stacked"></i>
                            <span>В наличии: <strong>${book.stock} шт.</strong></span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-clock"></i>
                            <span>Добавлено: ${formatDate(book.created_at)}</span>
                        </div>
                    </div>
                    <div class="book-detail-description">
                        <h3>Описание</h3>
                        <p>${escapeHtml(book.description || "Описание отсутствует")}</p>
                    </div>
                    <div class="book-actions">
                        ${addToCartBtn}
                        <button class="btn btn-outline" onclick="showPage('books')">
                            <i class="fas fa-arrow-left"></i> Назад к каталогу
                        </button>
                    </div>
                </div>
            </div>
            <div class="reviews-section" id="reviews-section">
                <h3><i class="fas fa-star"></i> Отзывы</h3>
                <div id="reviews-list">
                    <div class="loading"><i class="fas fa-spinner fa-spin"></i> Загрузка отзывов...</div>
                </div>
            </div>
            ${
              token
                ? `
                <div class="review-form">
                    <h3>Оставить отзыв</h3>
                    <form onsubmit="submitReview(event)">
                        <div class="form-group">
                            <label for="review-rating">
                                <i class="fas fa-star"></i> Оценка
                            </label>
                            <select id="review-rating" required>
                                <option value="5">⭐⭐⭐⭐⭐ Отлично</option>
                                <option value="4">⭐⭐⭐⭐ Хорошо</option>
                                <option value="3">⭐⭐⭐ Нормально</option>
                                <option value="2">⭐⭐ Плохо</option>
                                <option value="1">⭐ Ужасно</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="review-comment">
                                <i class="fas fa-comment"></i> Комментарий
                            </label>
                            <textarea id="review-comment" rows="4" placeholder="Поделитесь своим мнением о книге..."></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-paper-plane"></i> Отправить отзыв
                        </button>
                    </form>
                </div>
            `
                : `
                <div class="review-form">
                    <p class="text-center">
                        <i class="fas fa-info-circle"></i>
                        Войдите в систему, чтобы оставить отзыв
                    </p>
                    <button class="btn btn-primary btn-block" onclick="showLoginModal()">
                        <i class="fas fa-sign-in-alt"></i> Войти
                    </button>
                </div>
            `
            }
        </div>
    `;
}

async function loadReviews(bookId) {
  const reviewsList = document.getElementById("reviews-list");

  try {
    const response = await fetchAPI(`/reviews/?book=${bookId}`);
    if (response.ok) {
      const data = await response.json();
      displayReviews(data.results);
    } else {
      reviewsList.innerHTML =
        '<p class="text-muted">Ошибка загрузки отзывов</p>';
    }
  } catch (error) {
    reviewsList.innerHTML = '<p class="text-muted">Ошибка соединения</p>';
  }
}

function displayReviews(reviews) {
  const reviewsList = document.getElementById("reviews-list");

  if (reviews.length === 0) {
    reviewsList.innerHTML =
      '<p class="text-muted">Отзывов пока нет. Будьте первым!</p>';
    return;
  }

  reviewsList.innerHTML = "";
  reviews.forEach((review) => {
    const reviewCard = document.createElement("div");
    reviewCard.className = "review-card";

    const stars = "⭐".repeat(review.rating);

    reviewCard.innerHTML = `
            <div class="review-header">
                <div>
                    <span class="review-author">
                        <i class="fas fa-user"></i> ${escapeHtml(review.user.username)}
                    </span>
                    <span class="review-rating">${stars}</span>
                </div>
                <span class="review-date">${formatDate(review.created_at)}</span>
            </div>
            <p class="review-comment">${escapeHtml(review.comment || "Без комментария")}</p>
        `;

    reviewsList.appendChild(reviewCard);
  });
}

async function submitReview(event) {
  event.preventDefault();

  if (!token) {
    showToast("Необходимо войти в систему", "warning");
    showLoginModal();
    return;
  }

  const rating = document.getElementById("review-rating").value;
  const comment = document.getElementById("review-comment").value;

  try {
    const response = await fetchAPI(
      "/reviews/",
      "POST",
      {
        book_id: currentBook.id,
        rating: parseInt(rating),
        comment,
      },
      true,
    );

    if (response.ok) {
      showToast("Отзыв отправлен!", "success");
      document.getElementById("review-comment").value = "";
      loadReviews(currentBook.id);
    } else {
      const error = await response.json();
      showToast(
        "Ошибка: " + (error.detail || "Не удалось отправить отзыв"),
        "error",
      );
    }
  } catch (error) {
    showToast("Ошибка соединения", "error");
  }
}

async function loadAuthors() {
  const authorsListDiv = document.getElementById("authors-list");
  authorsListDiv.innerHTML =
    '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Загрузка...</div>';

  try {
    const response = await fetchAPI(`/authors/?page_size=100`);
    if (response.ok) {
      const data = await response.json();
      displayAuthors(data.results);
    } else {
      authorsListDiv.innerHTML =
        '<p class="text-center text-muted">Ошибка загрузки авторов</p>';
    }
  } catch (error) {
    authorsListDiv.innerHTML =
      '<p class="text-center text-muted">Ошибка соединения</p>';
  }
}

function displayAuthors(authors) {
  const authorsListDiv = document.getElementById("authors-list");

  if (authors.length === 0) {
    authorsListDiv.innerHTML =
      '<p class="text-center text-muted">Авторы не найдены</p>';
    return;
  }

  authorsListDiv.innerHTML = "";
  authors.forEach((author) => {
    const authorCard = document.createElement("div");
    authorCard.className = "author-card";

    const initials = author.name
      .split(" ")
      .map((n) => n[0])
      .join("");

    authorCard.innerHTML = `
            <div class="author-avatar">${initials}</div>
            <h3 class="author-name">${escapeHtml(author.name)}</h3>
            <p class="author-bio">${escapeHtml(author.bio || "Биография не указана")}</p>
        `;

    authorsListDiv.appendChild(authorCard);
  });
}

async function loadAuthorsFilter() {
  try {
    const response = await fetchAPI("/authors/?page=1&page_size=100");
    if (response.ok) {
      const data = await response.json();
      const select = document.getElementById("author-filter");
      select.innerHTML = '<option value="">Все авторы</option>';

      data.results.forEach((author) => {
        const option = document.createElement("option");
        option.value = author.id;
        option.textContent = author.name;
        select.appendChild(option);
      });
    }
  } catch (error) {
    console.error("Ошибка загрузки авторов для фильтра:", error);
  }
}

function applyFilters() {
  const search = document.getElementById("search-input").value;
  const author = document.getElementById("author-filter").value;
  const ordering = document.getElementById("sort-select").value;

  currentFilters = { search, author, ordering };
  loadBooks(1);
}

function resetFilters() {
  document.getElementById("search-input").value = "";
  document.getElementById("author-filter").value = "";
  document.getElementById("sort-select").value = "";
  currentFilters = {};
  loadBooks(1);
}

function handleSearchKeyup(event) {
  if (event.key === "Enter") {
    applyFilters();
  }
}

function addToCart(bookId) {
  if (!token) {
    showToast("Войдите в систему для добавления в корзину", "warning");
    showLoginModal();
    return;
  }

  const existingItem = cart.find((item) => item.book_id === bookId);

  if (existingItem) {
    existingItem.quantity += 1;
    showToast("Количество увеличено", "success");
  } else {
    cart.push({
      book_id: bookId,
      quantity: 1,
      book: currentBook,
    });
    showToast("Добавлено в корзину!", "success");
  }

  localStorage.setItem("cart", JSON.stringify(cart));
  updateCartCount();
}

function updateCartCount() {
  const count = cart.reduce((sum, item) => sum + item.quantity, 0);
  document.getElementById("cart-count").textContent = count;
}

function showCart() {
  showPage("cart");
  renderCart();
}

async function renderCart() {
  const cartContent = document.getElementById("cart-content");

  if (cart.length === 0) {
    cartContent.innerHTML = `
            <div class="cart-empty">
                <i class="fas fa-shopping-cart"></i>
                <p>Корзина пуста</p>
                <button class="btn btn-primary" onclick="showPage('books')">
                    <i class="fas fa-book"></i> Перейти к каталогу
                </button>
            </div>
        `;
    return;
  }

  const bookDetails = await Promise.all(
    cart.map(async (item) => {
      if (!item.book || !item.book.title) {
        try {
          const response = await fetchAPI(`/books/${item.book_id}/`);
          if (response.ok) {
            const book = await response.json();
            item.book = book;
            return book;
          }
        } catch (error) {
          console.error("Ошибка загрузки книги:", error);
        }
      }
      return item.book;
    }),
  );

  let totalPrice = 0;
  let html = '<div class="cart-items">';

  cart.forEach((item, index) => {
    const book = item.book || {};
    const itemTotal = (book.price || 0) * item.quantity;
    totalPrice += itemTotal;

    const cartImageHtml = book.cover_image
      ? `<img src="${escapeHtml(book.cover_image)}" alt="${escapeHtml(book.title)}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 5px;">`
      : `<i class="fas fa-book"></i>`;

    html += `
            <div class="cart-item">
                <div class="cart-item-image">
                    ${cartImageHtml}
                </div>
                <div class="cart-item-info">
                    <h4>${escapeHtml(book.title || "Загрузка...")}</h4>
                    <p class="cart-item-author">${escapeHtml(book.author?.name || "")}</p>
                    <p class="cart-item-price-single">${book.price || 0} ₽</p>
                </div>
                <div class="cart-item-quantity">
                    <button class="quantity-btn" onclick="changeQuantity(${index}, -1)">
                        <i class="fas fa-minus"></i>
                    </button>
                    <span class="quantity-value">${item.quantity}</span>
                    <button class="quantity-btn" onclick="changeQuantity(${index}, 1)">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
                <div class="cart-item-price">
                    ${itemTotal} ₽
                </div>
                <button class="cart-item-remove" onclick="removeFromCart(${index})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
  });

  html += "</div>";

  html += `
        <div class="cart-summary">
            <h3>Итого</h3>
            <div class="summary-row">
                <span>Товаров:</span>
                <span>${cart.reduce((sum, item) => sum + item.quantity, 0)} шт.</span>
            </div>
            <div class="summary-row">
                <span>Сумма:</span>
                <span>${totalPrice} ₽</span>
            </div>
            <div class="summary-total">
                <span>Итого:</span>
                <span>${totalPrice} ₽</span>
            </div>
            <button class="btn btn-primary checkout-btn" onclick="createOrder()">
                <i class="fas fa-check"></i> Оформить заказ
            </button>
        </div>
    `;

  cartContent.innerHTML = html;
}

function changeQuantity(index, delta) {
  cart[index].quantity += delta;

  if (cart[index].quantity <= 0) {
    cart.splice(index, 1);
  }

  localStorage.setItem("cart", JSON.stringify(cart));
  updateCartCount();
  renderCart();
}

function removeFromCart(index) {
  cart.splice(index, 1);
  localStorage.setItem("cart", JSON.stringify(cart));
  updateCartCount();
  renderCart();
  showToast("Товар удален из корзины", "info");
}

async function createOrder() {
  if (!token) {
    showToast("Необходимо войти в систему", "warning");
    showLoginModal();
    return;
  }

  if (cart.length === 0) {
    showToast("Корзина пуста", "warning");
    return;
  }

  const items = cart.map((item) => ({
    book_id: item.book_id,
    quantity: item.quantity,
  }));

  try {
    const response = await fetchAPI("/create-order/", "POST", { items }, true);

    if (response.ok) {
      cart = [];
      localStorage.setItem("cart", JSON.stringify(cart));
      updateCartCount();
      showToast("Заказ успешно оформлен!", "success");
      showPage("orders");
    } else {
      const error = await response.json();
      showToast(
        "Ошибка: " + (error.error || "Не удалось оформить заказ"),
        "error",
      );
    }
  } catch (error) {
    showToast("Ошибка соединения", "error");
  }
}

async function loadOrders() {
  const ordersListDiv = document.getElementById("orders-list");
  ordersListDiv.innerHTML =
    '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Загрузка...</div>';

  try {
    const response = await fetchAPI(
      `/orders/?page_size=100`,
      "GET",
      null,
      true,
    );
    if (response.ok) {
      const data = await response.json();
      displayOrders(data.results);
    } else {
      ordersListDiv.innerHTML =
        '<p class="text-center text-muted">Ошибка загрузки заказов</p>';
    }
  } catch (error) {
    ordersListDiv.innerHTML =
      '<p class="text-center text-muted">Ошибка соединения</p>';
  }
}

function displayOrders(orders) {
  const ordersListDiv = document.getElementById("orders-list");

  if (orders.length === 0) {
    ordersListDiv.innerHTML = `
            <div class="cart-empty">
                <i class="fas fa-shopping-bag"></i>
                <p>У вас пока нет заказов</p>
                <button class="btn btn-primary" onclick="showPage('books')">
                    <i class="fas fa-book"></i> Перейти к каталогу
                </button>
            </div>
        `;
    return;
  }

  ordersListDiv.innerHTML = "";
  orders.forEach((order) => {
    const orderCard = document.createElement("div");
    orderCard.className = "order-card";

    const statusClass = order.status;
    const statusText =
      {
        pending: "Ожидает",
        completed: "Завершен",
        cancelled: "Отменен",
      }[order.status] || order.status;

    let itemsHtml = "";
    order.items.forEach((item) => {
      itemsHtml += `
                <div class="order-item">
                    <span class="order-item-name">${escapeHtml(item.book.title)}</span>
                    <span class="order-item-quantity">${item.quantity} шт.</span>
                    <span class="order-item-price">${item.price * item.quantity} ₽</span>
                </div>
            `;
    });

    orderCard.innerHTML = `
            <div class="order-header">
                <span class="order-id">
                    <i class="fas fa-receipt"></i> Заказ #${order.id}
                </span>
                <span class="order-status ${statusClass}">${statusText}</span>
            </div>
            <div class="order-items">
                ${itemsHtml}
            </div>
            <div class="order-footer">
                <span class="order-date">
                    <i class="fas fa-calendar"></i> ${formatDate(order.created_at)}
                </span>
                <span class="order-total">${order.total_price} ₽</span>
            </div>
        `;

    ordersListDiv.appendChild(orderCard);
  });
}

function displayPagination(data, prefix, loadFunction) {
  const paginationDiv = document.getElementById(`${prefix}-pagination`);
  if (paginationDiv) {
    paginationDiv.innerHTML = "";
  }
}

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  const icons = {
    success: "fa-check-circle",
    error: "fa-exclamation-circle",
    warning: "fa-exclamation-triangle",
    info: "fa-info-circle",
  };

  toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <span>${escapeHtml(message)}</span>
    `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "slideInRight 0.3s ease reverse";
    setTimeout(() => {
      container.removeChild(toast);
    }, 300);
  }, 3000);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatDate(dateString) {
  const date = new Date(dateString);
  const options = {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  };
  return date.toLocaleDateString("ru-RU", options);
}
