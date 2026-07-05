pkgname=annotatia
pkgver=1.0.0
pkgrel=1
pkgdesc='Convert Japanese text to LaTeX with furigana (\ruby) annotation'
arch=('any')
url=''
license=('MIT')
depends=('python' 'python-pykakasi')
makedepends=('python-build' 'python-installer' 'python-wheel')
source=("file://${PWD}/pyproject.toml" "file://${PWD}/src/$pkgname.py")
md5sums=('SKIP'
         'SKIP')

build() {
    cd "$srcdir"
    mkdir -p src
    mv "$pkgname.py" src/
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir"
    python -m installer --destdir="$pkgdir" dist/*.whl
}
