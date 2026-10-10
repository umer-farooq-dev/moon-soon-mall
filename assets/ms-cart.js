// MoonSoon cart helpers: add buttons ([data-ms-add]), quantity offers, free gift auto add/remove.
// Uses Horizon's CartLinesUpdateEvent so the cart drawer, cart icon and cart page refresh themselves.
import { CartLinesUpdateEvent, StandardEvents } from '@shopify/events';

const sectionIds = () =>
  [...document.querySelectorAll('cart-items-component')].map((el) => el.dataset.sectionId).filter(Boolean).join(',');

const getCart = () => fetch(`${Theme.routes.cart_url}.js`).then((r) => r.json());

let busy = false;

/**
 * Runs a cart request and tells Horizon about it.
 * @param {HTMLElement} source - element the event is dispatched from
 * @param {'add'|'update'|'remove'} action
 * @param {string} url
 * @param {object} body
 * @param {Array<object>} lines
 */
async function cartRequest(source, action, url, body, lines) {
  const deferred = CartLinesUpdateEvent.createPromise();
  source.dispatchEvent(
    new CartLinesUpdateEvent({ action, context: 'product', lines, promise: deferred.promise })
  );
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ ...body, sections: sectionIds(), sections_url: window.location.pathname }),
    }).then((r) => r.json());
    const cart = await getCart();
    deferred.resolve({
      cart: CartLinesUpdateEvent.createCartFromAjaxResponse(cart),
      detail: { items: cart.items, sections: res.sections, didError: Boolean(res.status), source: 'ms-cart' },
    });
    return res;
  } catch (error) {
    deferred.reject(error);
  }
}

// Add buttons: pair-it-with, cart upsells
document.addEventListener('click', async (event) => {
  const btn = event.target instanceof Element ? event.target.closest('[data-ms-add]') : null;
  if (!btn || btn.disabled) return;
  event.preventDefault();
  btn.disabled = true;
  btn.classList.add('is-loading');
  const id = Number(btn.dataset.msAdd);
  await cartRequest(btn, 'add', Theme.routes.cart_add_url, { items: [{ id, quantity: 1 }] }, [
    { merchandiseId: String(id), quantity: 1 },
  ]);
  btn.disabled = false;
  btn.classList.remove('is-loading');
});

// Quantity offers: selected box sets the product form quantity
document.addEventListener('change', (event) => {
  const input = event.target;
  if (!(input instanceof HTMLInputElement) || !input.closest('[data-ms-offers]')) return;
  const scope = input.closest('.shopify-section') || document;
  const form = scope.querySelector('product-form-component form, form[action*="/cart/add"]');
  if (!form) return;
  let qty = form.querySelector('input[name="quantity"]');
  if (!qty) {
    qty = document.createElement('input');
    qty.type = 'hidden';
    qty.name = 'quantity';
    form.append(qty);
  }
  qty.value = input.value;
  scope.querySelectorAll('[data-ms-atc-price]').forEach((el) => (el.textContent = ` - ${input.dataset.price}`));
  qty.dispatchEvent(new Event('input', { bubbles: true }));
  qty.dispatchEvent(new Event('change', { bubbles: true }));
});

// Free gift: add when the cart reaches the goal, remove when it drops below
async function syncGift() {
  const config = window.MoonSoonCart;
  if (!config?.giftVariant || !config.giftThreshold || busy) return;
  busy = true;
  try {
    const cart = await getCart();
    const gift = cart.items.find((item) => item.variant_id === config.giftVariant);
    const total = cart.items_subtotal_price - (gift ? gift.final_line_price : 0);
    const source = document.querySelector('cart-items-component') || document.body;
    if (total >= config.giftThreshold && !gift) {
      await cartRequest(
        source,
        'add',
        Theme.routes.cart_add_url,
        { items: [{ id: config.giftVariant, quantity: 1, properties: { _gift: 'free' } }] },
        [{ merchandiseId: String(config.giftVariant), quantity: 1 }]
      );
    } else if (gift && (total < config.giftThreshold || gift.quantity > 1)) {
      const quantity = total < config.giftThreshold ? 0 : 1;
      await cartRequest(source, quantity ? 'update' : 'remove', Theme.routes.cart_change_url, { id: gift.key, quantity }, [
        { id: gift.key, quantity },
      ]);
    }
  } finally {
    busy = false;
  }
}

document.addEventListener(StandardEvents.cartLinesUpdate, (event) => {
  if (busy) return;
  event.promise?.then(syncGift).catch(() => {});
});

if (window.MoonSoonCart?.giftVariant) syncGift();
