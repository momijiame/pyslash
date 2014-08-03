pyslash
=======

Python Script for Libvirt Acceleration SHortcut 

# これは何？

Libvirt API を実行するコマンドラインツールです。

## virsh と何が違うの？

pyslash は virsh に実装されていない機能の実装や、複雑な手順が必要な機能の単純化を目指しています。

# インストール

## 事前準備

インストールには事前に以下がシステムにインストールされている必要があります。

* Python
* PIP
* Libvirt

## ソースコードからインストールする

```
# pip install git+https://github.com/momijiame/pyslash.git
```

## PyPI からインストールする

```
# pip install pyslash
```

# 使い方

例えば動作中のドメインが持つ TAP インターフェースの一覧を得たい場合には以下のように 'tap-list' サブコマンドを実行します。
遠隔にある Libvirt に接続する場合は URI を -c オプションで指定してください。
```
$ slash -c "qemu+ssh://kvm/system?socket=/var/run/libvirt/libvirt-sock" tap-list
+-------+--------------+---------+---------+-------------------+--------+
|  Tap  |    Domain    | Network |   Type  |       HWAddr      | Model  |
+-------+--------------+---------+---------+-------------------+--------+
| vnet1 |   multinic   | default | network | 52:54:00:c8:84:e8 | virtio |
| vnet2 |   multinic   |  public |  bridge | 52:54:00:08:b3:8f | virtio |
| vnet0 | centos6-base | default | network | 52:54:00:af:d1:d2 | virtio |
+-------+--------------+---------+---------+-------------------+--------+
```

デフォルトでは結果がテーブルで得られますが、それではシステムから扱いづらいこともあるでしょう。
その場合には -f オプションに "json" を指定することで JSON 形式で結果を得ることができます。
```
$ slash -f "json" -c "qemu+ssh://kvm/system?socket=/var/run/libvirt/libvirt-sock" tap-list
[
    {
        "name": "vnet1",
        "domain": "multinic",
        "network": "default",
        "type": "network",
        "hwaddr": "52:54:00:c8:84:e8",
        "model": "virtio"
    },
    {
        "name": "vnet2",
        "domain": "multinic",
        "network": "public",
        "type": "bridge",
        "hwaddr": "52:54:00:08:b3:8f",
        "model": "virtio"
    },
    {
        "name": "vnet0",
        "domain": "centos6-base",
        "network": "default",
        "type": "network",
        "hwaddr": "52:54:00:af:d1:d2",
        "model": "virtio"
    }
]

```
