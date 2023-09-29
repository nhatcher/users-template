
export default function getCookie(value) {
    let cookies = {};
    document.cookie.split(';').forEach(s => {
        const cookie = s.split('=');
        cookies[cookie[0].trim()]= cookie[1].trim();
    });
    return cookies[value];
}