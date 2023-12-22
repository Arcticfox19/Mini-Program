<template>
	<view>
		<view class='facechange'>
			<image :src="srcImg" mode="aspectFit"></image>
			<video :src="resvideo"></video>
			<button @click="chooseImage">Upload Image to Server</button>
			<button @click="creatVideo">Generate Face Swap Video</button>
			<!-- <button @click="getVideo">获取后端返回的视频并显示</button> -->
		</view>
	</view>
</template>
<script>
	export default {
		
		data(){
			return {
				srcImg:'',
				resvideo:'',
				text:'',
				count: 0
			}
		},
		methods:{
			//选择图片，调用uni.chooseImage
			chooseImage(){
				let vm = this;
				uni.chooseImage({
					count:1,	//设置选择图片数量为1
					success:(res) => {	//选择图片成功后会执行success回调函数
						//获取选择图片的临时路径
						const tempFilePaths = res.tempFilePaths
						//设置srcImg的URL
						vm.srcImg = tempFilePaths[0]
						//选择完图片后，将该图片上传到后端，调用uni.uploadFile
						uni.uploadFile({
							//url为后端服务器的接口，这里需要填写你自己的接口地址
							url:"http://192.168.31.24:8088/getSrcImg",
							//文件类型为image
							fileType:"image",
							//文件路径为选择图片的临时路径
							filePath: tempFilePaths[0],
							//文件对应的key，在后端通过这个key可以获取到文件的二进制内容
							name:'srcImg',
							//上传成功会执行success回调函数
							success: (uploadFileRes) => {
								//在控制台输出后端返回的数据
								console.log(uploadFileRes.data)
							}
						})
					}
				})
			},
			creatVideo(){
				let vm = this
				let time = parseInt(new Date().getTime() / 1000) + '';
								console.log(time)
				
				uni.request({
					//url为后端服务器的接口，这里需要填写你自己的接口地址
					url:"http://192.168.31.24:8088/faceChange/"+vm.count,
					//url:"http://192.168.0.105:8088/faceChange/"+vm.count,
					timeout:6000000000,
					success: (res) => {
						if(res.statusCode===200){
							vm.resvideo="http://192.168.31.24:8088/getVideo/"+ vm.count
							//vm.resvideo="http://192.168.0.105:8088/getVideo/"+ vm.count
							vm.count++
							uni.showToast({
								title: "Face Swap Video Generated!",
								duration: 4000
							})
						}
						console.log(res.data)
						}
					})
				},
			// getVideo(){
			// 	let vm = this
			// 	//调用uni.request，发起网络请求
			// 	uni.request({
			// 		//url为后端服务器的接口，这里需要填写你自己的接口地址
			// 		url:"http://192.168.0.105:8088/queryVideo/"+ vm.count,
			// 		success: (res) => {
			// 			if(res.statusCode==200){
			// 				vm.resvideo="http://192.168.0.105:8088/getVideo/"+ vm.count
			// 				vm.count++
			// 			}
			// 			console.log(res.data)
			// 			}
			// 		})
			// 	}
		}
	}
</script>
<style>
	.facechange{
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;	
		margin-bottom: 200px;
	}
</style>