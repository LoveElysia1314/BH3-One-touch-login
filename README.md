注意：不要将本程序置于含中文的文件路径中。
操作顺序
首次使用：
0.安装需要的所有库
1.需要有PC端崩坏三扫码器(即本项目的main.py，或编译好的exe文件，下载链接：https://haocen.lanzoum.com/b01ovffcj，密码193x，感谢github用户@Haocen2004)
2.打开扫码器并登录
3.以管理员身份运行程序，按照提示输扫码器路径和游戏本体(非扫码器)
4.正常情况下，应当能够自动将登录方式改为二维码、有资源时自动下载、检测到有“崩坏3”窗口时自动扫码、自动进入游戏并关闭本程序和扫码器。
注意：由于自动进入游戏并关闭本程序和扫码器功能依赖于识别的目标图像包含文字，而由于文字大小不仅与屏幕宽有关，还与字体大小、屏幕缩放倍率有关，故兼容性有问题。遇到这个情况，则需要参考.\Pictures_to_Match\Defaul文件夹中的“8000p_4.png”，运行游戏并在“点击任意处进入游戏”的界面截图并裁剪，将裁剪好的图片替换程序自动依据屏幕分辨率生成的图片。
（例如，显示器的分辨率是2560x1440，则将裁切好的文件素材命名为“1440p_4”，放入.\Pictures_to_Match\1440p文件夹替换原有图片）

配置好后，以后仅需要运行程序即可一键进入游戏。



程序原理：
BH3MatchPicture.py实现目标图片匹配和模拟点击和扫码。
BH3_Bilibili.py是主程序，实现打开扫码器和游戏，并调用BH3MatchPicture.py，在检测到“崩坏3”窗口时进行图像识别和扫码，以及自动关闭扫码器。
当程序在截屏中检测到相似部分时，将自动点击匹配到部分的中心坐标，从而实现将登陆方式从账密改为扫码(即模拟点击登录框坐上角的二维码图标)、需要下载文件的自动确认、扫码成功后进入游戏以及关闭程序。

程序逻辑：
先读取json文件，获取扫码器文件路径和官服崩坏三文件路径，并尝试打开。如不能打开，则要求用户输入文件路径，程序将其存入json文件，并再次打开扫码器和游戏。接着，创建主窗口，设置控件大小。点击按钮可以手动拷屏，但无法关闭扫码器。
然后每秒循环一次：
首先检测是否有"崩坏三窗口"(防止挂着程序抢邦邦码)：
	“若是，是否已经扫码”状态检测：
		>>若否，识别屏幕画面是否含目标图像：
			>>若是，点击对应图片的中心坐标；
			>>若否，检测屏幕是否有二维码，
				>>若是，拷屏，并将“是否已经扫码”状态设为是。
		>>若是，识别屏幕画面是否含目标图像：
			>>若是，点击对应图片的中心坐标进入游戏，关闭扫码器和提示窗口。


程序编译后若无法运行，将"libzbar-64.dll"和"libiconv.dll"文件放入程序相同目录试试。
