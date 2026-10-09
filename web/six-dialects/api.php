<?php
/*
 * Six Dialects · relay to Public AI
 *
 * Public AI does not allow browsers to call it directly (no CORS headers),
 * so the page at eofe.ai/six-dialects/ sends its request here, on the same
 * domain, and this file passes it on.
 *
 * It does one thing. It takes the visitor's own key from the request, forwards
 * the chat request to Public AI, and hands back the answer. It stores nothing,
 * writes nothing to disk and logs nothing. It only talks to one address and
 * only with one model, so it cannot be used as an open relay.
 */

const UPSTREAM   = 'https://api.publicai.co/v1/chat/completions';
const MODELS     = ['swiss-ai/apertus-v1.5-70b'];
const MAX_BODY   = 60000;   // bytes. The prompt with a long description is about 12 000.
const MAX_TOKENS = 2000;    // same ceiling as the command line review
const ALLOWED_HOSTS = ['eofe.ai', 'www.eofe.ai'];

// for local testing only: SIXD_UPSTREAM points the relay at a fake server
if (getenv('SIXD_UPSTREAM')) {
    define('TARGET', getenv('SIXD_UPSTREAM'));
    $ALLOWED = array_merge(ALLOWED_HOSTS, ['localhost', '127.0.0.1']);
} else {
    define('TARGET', UPSTREAM);
    $ALLOWED = ALLOWED_HOSTS;
}

@set_time_limit(180);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

function fail(int $code, string $msg): void {
    http_response_code($code);
    echo json_encode(['error' => ['message' => $msg]]);
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    fail(405, 'POST only');
}

// same-site requests only: the browser always sends Origin on a POST fetch
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
$host = $origin ? parse_url($origin, PHP_URL_HOST) : '';
if (!$host || !in_array(strtolower($host), $ALLOWED, true)) {
    fail(403, 'this relay only serves the Six Dialects page');
}

$key = trim($_SERVER['HTTP_X_PUBLICAI_KEY'] ?? '');
if ($key === '' || strlen($key) > 400 || preg_match('/[\r\n]/', $key)) {
    fail(401, 'missing or malformed key');
}

$raw = file_get_contents('php://input', false, null, 0, MAX_BODY + 1);
if ($raw === false || strlen($raw) > MAX_BODY) {
    fail(413, 'that description is too long');
}

$in = json_decode($raw, true);
if (!is_array($in) || !isset($in['messages']) || !is_array($in['messages'])) {
    fail(400, 'could not read the request');
}
if (!in_array($in['model'] ?? '', MODELS, true)) {
    fail(400, 'model not served by this relay');
}

// rebuild the request from known fields only
$out = [
    'model'       => $in['model'],
    'messages'    => array_values(array_map(function ($m) {
        return ['role' => (string)($m['role'] ?? ''), 'content' => (string)($m['content'] ?? '')];
    }, array_slice($in['messages'], 0, 4))),
    'temperature' => max(0, min(1, (float)($in['temperature'] ?? 0.2))),
    'max_tokens'  => max(1, min(MAX_TOKENS, (int)($in['max_tokens'] ?? MAX_TOKENS))),
];
$body = json_encode($out);

$headers = [
    'Content-Type: application/json',
    'Authorization: Bearer ' . $key,
    // Public AI rejects generic client agents as bot traffic
    'User-Agent: six-dialects-web/0.1 (+https://eofe.ai/six-dialects/)',
];

if (function_exists('curl_init')) {
    $ch = curl_init(TARGET);
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => $body,
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_TIMEOUT        => 170,
    ]);
    $resp = curl_exec($ch);
    $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $err  = curl_error($ch);
    curl_close($ch);
} else {
    $ctx = stream_context_create(['http' => [
        'method'        => 'POST',
        'header'        => implode("\r\n", $headers),
        'content'       => $body,
        'timeout'       => 170,
        'ignore_errors' => true,
    ]]);
    $resp = @file_get_contents(TARGET, false, $ctx);
    $code = 0;
    foreach ($http_response_header ?? [] as $h) {
        if (preg_match('#^HTTP/\S+\s+(\d{3})#', $h, $m)) $code = (int)$m[1];
    }
    $err = $resp === false ? 'no response' : '';
}

if ($resp === false || $code === 0) {
    fail(502, 'Public AI did not answer' . ($err ? ': ' . $err : ''));
}

http_response_code($code);
echo $resp;
