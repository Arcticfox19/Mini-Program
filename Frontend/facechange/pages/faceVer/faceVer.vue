<template>
	<view>
		<view class='facever'>
			<image :src="Img1" mode="aspectFit"></image>
			<text>\n</text>
			<image :src="Img2" mode="aspectFit"></image>
			<text>\n</text>
			<text style="font-size:20px">{{text}}</text>
			<button @click="chooseImage1">Upload Image No.1 to Server</button>
			<button @click="chooseImage2">Upload Image No.2 to Server</button>
			<button @click="getResult">Perform Facial Verification</button>
		</view>
		
	</view>
</template>

<script>
	export default {
		data(){
			return {
				Img1:'',
				Img2:'',
				text:''
			}
		},
		methods:{
			//选择图片，调用uni.chooseImage
			chooseImage1(){
				let vm = this;
				uni.chooseImage({
					count:2,	//设置选择图片数量为1
					success:(res) => {	//选择图片成功后会执行success回调函数
						//获取选择图片的临时路径
						const tempFilePaths = res.tempFilePaths
						//设置srcImg的URL
						vm.Img1 = tempFilePaths[0]
						//选择完图片后，将该图片上传到后端，调用uni.uploadFile
						uni.uploadFile({
							//url为后端服务器的接口，这里需要填写你自己的接口地址
							url:"http://192.168.31.24:8088/getImg1",
							//文件类型为image
							fileType:"image",
							//文件路径为选择图片的临时路径
							filePath: tempFilePaths[0],
							//文件对应的key，在后端通过这个key可以获取到文件的二进制内容
							name:'Img1',
							//上传成功会执行success回调函数
							success: (uploadFileRes) => {
								//在控制台输出后端返回的数据
								console.log(uploadFileRes.data)
							}
						})
					}
				})
			},
			chooseImage2(){
				let vm = this;
				uni.chooseImage({
					count:1,	//设置选择图片数量为1
					success:(res) => {	//选择图片成功后会执行success回调函数
						//获取选择图片的临时路径
						const tempFilePaths = res.tempFilePaths
						//设置srcImg的URL
						vm.Img2 = tempFilePaths[0]
						//选择完图片后，将该图片上传到后端，调用uni.uploadFile
						uni.uploadFile({
							//url为后端服务器的接口，这里需要填写你自己的接口地址
							url:"http://192.168.31.24:8088/getImg2",
							//文件类型为image
							fileType:"image",
							//文件路径为选择图片的临时路径
							filePath: tempFilePaths[0],
							//文件对应的key，在后端通过这个key可以获取到文件的二进制内容
							name:'Img2',
							//上传成功会执行success回调函数
							success: (uploadFileRes) => {
								//在控制台输出后端返回的数据
								console.log(uploadFileRes.data)
							}
						})
					}
				})
			},
			getResult(){
					let vm = this
					//调用uni.request，发起网络请求
					uni.request({
						//url为后端服务器的接口，这里需要填写你自己的接口地址
						url:"http://192.168.31.24:8088/verify",
						//若后端传来的图片是二进制流，需要设置responseType为arraybuffer。若为base64码，则无需设置
						responseType:'string',
						success: (res) => {
							if(res.statusCode===200){
								uni.showToast({
									title: "Verification Completed",
									duration: 2000
								})
							}
							vm.text ="Facial Verification Result:"+res.data
							}
							})
					}
			}
		}
</script>

<style>
	.facever{
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;	
		margin-bottom: 200px;
	}
</style>